import pathlib
import shutil
from functools import cached_property

from utils import SECONDS_IN, TIME_FORMAT_TIME, File, Log, Time, get_time_id

from news_lk_bulletin.core.NewsArticle import NewsArticle
from utils_future import LLM

log = Log('NewsArticleBulletin')


class NewsBulletin:
   

    def __init__(self, llm: LLM):
        self.llm = llm

    @staticmethod
    def get_article_blurb(news_article: NewsArticle) -> str:
        if news_article.en_title is None:
            return None
        article_lines = []
        article_lines.append('# ' + news_article.en_title)
        article_lines.append(f'*{news_article.time_str}*')
        article_lines.append(
            f'[{news_article.newspaper_id}]({news_article.url})'
        )
        body_lines = news_article.en_body_lines_shorter
        article_lines.extend(body_lines)
        article_lines.append('')
        article_blurb = '\n\n'.join(article_lines)
        return article_blurb

    @cached_property
    def blurb(self) -> str:
        news_article_list = NewsArticle.list_all()
        log.debug(f'Loaded {len(news_article_list)} news articles')

        lines = []
        n_total = 0
        used_articles = []
        for news_article in news_article_list:
            article_blurb = NewsBulletin.get_article_blurb(news_article)
            if not article_blurb:
                continue

            n_article = len(article_blurb)
            if n_total + n_article > LLM.MAX_DATA_BYTES:
                break
            n_total += n_article
            lines.append(article_blurb)
            used_articles.append(news_article)

        n_articles = len(used_articles)
        dt = used_articles[0].time_ut - used_articles[-1].time_ut
        dt_hours = dt / SECONDS_IN.HOUR
        lines = [
            f'Based on **{n_articles:,}** News Articles,'
            + f' from the last **{dt_hours:.0f}** hours.'
        ] + lines

        return '\n\n'.join(lines)

    @cached_property
    def system_cmd(self) -> str:
        return ' '.join(
            [
                'Extract objective facts from this set of news articles,',
                'that might be of practical use to ordinary Sri Lankans,'
                'and present as 10 detailed bullets.',
                'EXCLUDE news not directly relevant to Sri Lanka.',
                'DO NOT duplicate repeat news articles.',
                'EXCLUDE political opinions/statements by politicians.',
                'EXCLUDE marketing/propaganda.',
                DO mention the name of the source, as "[newspaper]".',
                'EMPHASIZE named entities and statistics in bold.',
            ]
        )

    @cached_property
    def bulletin(self) -> str:
        self.llm.append('system', self.system_cmd)
        self.llm.append('user', self.blurb)
        bulletin = self.llm.send()
        bulletin = bulletin.replace('Source:', '')
        return bulletin

    @cached_property
    def path(self) -> pathlib.Path:
        time_id = get_time_id()
        return pathlib.Path('data', f'{time_id}.md')

    @cached_property
    def all_lines(self) -> list[str]:
        time_str = TIME_FORMAT_TIME.stringify(Time.now())

        return [
            '# #SriLanka :sri_lanka: News Bulletin',
            '',
            '<div id="news_lk_bulletin">',
            '',
            f'*Updated* **{time_str}**',
            '',
            self.bulletin,
            '',
            '</div>',
            '',
            '[Previous](data) Bulletins',
            '',
            '## Methodology',
            '',
            'This bulletin has been autogenerated by OpenAI\'s'
            + f' [{LLM.DEFAULT_MODEL}]({LLM.DEFAULT_MODEL_URL})'
            + ' model, with the following prompt:',
            '',
            f'*{self.system_cmd}*',
            '',
            '## Source News',
            '',
            self.blurb,
        ]

    def write(self):
        File(self.path).write_lines(self.all_lines)
        log.info(f'Wrote news bulletin to {self.path}')

        # copy to readme
        readme_path = pathlib.Path('README.md')
        shutil.copy(self.path, readme_path)
        log.info('Wrote news bulletin to README.md')
