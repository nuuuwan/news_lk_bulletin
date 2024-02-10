import pathlib
import tempfile
from dataclasses import dataclass
from functools import cached_property

from utils import JSONFile, Log, TSVFile

from utils_future import WWW

log = Log('NewsArticle')


@dataclass
class NewsArticle:
    newspaper_id: str
    time_str: str
    original_title: str
    n_original_body_lines: int  # noqa
    hash: str
    time_ut: float
    original_lang: str
    url: str

    URL_SUMMARY = (
        'https://raw.githubusercontent.com'
        + '/nuuuwan/news_lk3_data/main/summary.tsv'
    )
    TEMP_SUMMARY_PATH = pathlib.Path(tempfile.gettempdir(), 'summary.tsv')

    @staticmethod
    def from_dict(d: dict):
        return NewsArticle(
            d['newspaper_id'],
            d['time_str'],
            d['original_title'],
            int(d['n_original_body_lines']),
            d['hash'],
            float(d['time_ut']),
            d['original_lang'],
            d['url'],
        )

    @cached_property
    def url_detailed_data(self) -> str:
        return (
            'https://raw.githubusercontent.com'
            + '/nuuuwan/news_lk3_data/main/articles'
            + f'/{self.hash}.json'
        )

    @cached_property
    def detailed_data_path(self) -> str:
        return pathlib.Path(
            tempfile.gettempdir(), f'news_lk.{self.hash}.json'
        )

    @cached_property
    def detailed_data(self) -> dict:
        WWW(self.url_detailed_data).download(self.detailed_data_path)
        return JSONFile(self.detailed_data_path).read()

    @cached_property
    def original_body_lines(self) -> list[str]:
        return self.detailed_data['original_body_lines']

    @cached_property
    def original_body_lines_shorter(self) -> list[str]:
        MAX_CHARS = 512
        n_total = 0
        lines = []
        for line in self.original_body_lines:
            n_line = len(line)
            if n_total + n_line > MAX_CHARS:
                lines.append('...')
                break
            n_total += n_line
            lines.append(line)
        return lines

    @staticmethod
    def download_summary():
        www = WWW(NewsArticle.URL_SUMMARY)
        www.download(NewsArticle.TEMP_SUMMARY_PATH)

    @staticmethod
    def get_summary_list() -> list[dict]:
        NewsArticle.download_summary()
        d_list = TSVFile(NewsArticle.TEMP_SUMMARY_PATH).read()
        n = len(d_list)
        log.info(
            f'Loaded {n:,} news articles from {NewsArticle.TEMP_SUMMARY_PATH}'
        )
        return d_list

    @staticmethod
    def list_all() -> list['NewsArticle']:
        d_list = NewsArticle.get_summary_list()
        news_article_list = [NewsArticle.from_dict(d) for d in d_list]
        sorted_news_article_list = sorted(
            news_article_list, key=lambda x: x.time_ut, reverse=True
        )
        return sorted_news_article_list
