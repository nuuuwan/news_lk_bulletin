import pathlib
import shutil
import random
from functools import cached_property

from utils import TIME_FORMAT_TIME, File, Log, Time, get_time_id

from news_lk_bulletin.core.NewsArticle import NewsArticle
from utils_future import LLM

log = Log('NewsArticleBulletin')


class NewsBulletin:
    def __init__(self, llm: LLM, max_articles, max_data_bytes: int):
        self.llm = llm
        self.max_articles = max_articles
        self.max_data_bytes = max_data_bytes

    @cached_property
    def blurb(self) -> str:
        news_article_list = NewsArticle.list_all()
        en_news_article_list = [
            news_article
            for news_article in news_article_list
            if news_article.original_lang == 'en'
        ]
        recent_news_article_list = en_news_article_list[: self.max_articles]
        random.shuffle(recent_news_article_list)

        lines = []
        n_total = 0
        for news_article in recent_news_article_list:
            article_lines = []
            article_lines.append('# ' + news_article.original_title)
            article_lines.append(f'*{news_article.time_str}*')
            article_lines.append(
                f'[{news_article.newspaper_id}]({news_article.url})'
            )
            article_lines.extend(news_article.original_body_lines)
            article_lines.append('')
            article_blurb = '\n\n'.join(article_lines)
            n_article = len(article_blurb)
            if n_total + n_article > self.max_data_bytes:
                break
            n_total += n_article
            lines.append(article_blurb)

        return '\n\n'.join(lines)

    @cached_property
    def system_cmd(self) -> str:
        return ' '.join(
            [
                'Summarize the following set of news articles',
                'into 10 bullets.',
                'DO NOT repeat facts.',
                'DO use emojis, handles and hashtags for a better readability.',
                'DO prioritize facts over opinions.',
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
            f'*Updated* **{time_str}**',
            '',
            self.bulletin,
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
