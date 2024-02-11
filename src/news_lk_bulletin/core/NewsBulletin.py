import pathlib
import shutil
from functools import cached_property

from utils import TIME_FORMAT_TIME, File, Log, Time, get_time_id, SECONDS_IN

from news_lk_bulletin.core.NewsArticle import NewsArticle
from utils_future import LLM

log = Log('NewsArticleBulletin')


class NewsBulletin:
    MAX_DATA_BYTES = 28_000

    def __init__(self, llm: LLM):
        self.llm = llm

    @cached_property
    def blurb(self) -> str:
        news_article_list = NewsArticle.list_all()
        news_article_list = [
            news_article
            for news_article in news_article_list
            if news_article.original_lang == 'en'
        ]

        lines = []
        n_total = 0
        used_articles = []
        for news_article in news_article_list:
            article_lines = []
            article_lines.append('# ' + news_article.original_title)
            article_lines.append(f'*{news_article.time_str}*')
            article_lines.append(
                f'[{news_article.newspaper_id}]({news_article.url})'
            )
            body_lines = news_article.original_body_lines_shorter
            article_lines.extend(body_lines)
            article_lines.append('')
            article_blurb = '\n\n'.join(article_lines)
            n_article = len(article_blurb)
            if n_total + n_article > NewsBulletin.MAX_DATA_BYTES:
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
                'Summarize the following set of news articles',
                'into 10 bullets.',
                'DO prioritize news that might be of practical use.',
                'SORT news by practical use to ordinary Sri Lankan citizens.'
                'DO prioritize facts over opinions.',
                'DO use emojis and Markdown Bold/Italics for readability.',
                'DO include named entities and statistics',
                'DO NOT repeat information.',
                'DO NOT quote sources.',
                'DO NOT include facts that seem marketing or propaganda.',
            ]
        )

    @cached_property
    def bulletin(self) -> str:
        self.llm.append('system', self.system_cmd)
        self.llm.append('user', self.blurb)
        return self.llm.send()

    @cached_property
    def path(self) -> pathlib.Path:
        time_id = get_time_id()
        return pathlib.Path('data', f'{time_id}.md')

    @cached_property
    def all_lines(self) -> list[str]:
        time_str = TIME_FORMAT_TIME.stringify(Time.now())

        return [
            '# #SriLanka🇱🇰 News Bulletin',
            '',
            '<div id="news_lk_bulletin">',
            f'*Updated* **{time_str}**',
            '',
            self.bulletin,
            '',
            '</div>',
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
