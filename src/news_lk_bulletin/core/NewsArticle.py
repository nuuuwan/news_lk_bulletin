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
    def url_extended_data(self) -> str:
        return (
            'https://raw.githubusercontent.com'
            + '/nuuuwan/news_lk3_data/main/ext_articles'
            + f'/{self.hash}.ext.json'
        )

    @cached_property
    def extended_data_path(self) -> str:
        return pathlib.Path(
            tempfile.gettempdir(), f'news_lk.{self.hash}.ext.json'
        )

    @cached_property
    def extended_data(self) -> dict:
        try:
            WWW(self.url_extended_data).download(self.extended_data_path)
            return JSONFile(self.extended_data_path).read()
        except BaseException:
            return None

    @cached_property
    def en_title(self) -> str:
        if self.original_lang == 'en':
            return self.original_title

        extended_data = self.extended_data
        if not extended_data:
            return None
        if 'translated_text' not in extended_data:
            return None
        if 'en' not in extended_data['translated_text']:
            return None
        return extended_data['translated_text']['en']['title']

    @cached_property
    def en_body_lines(self) -> list[str]:
        if self.original_lang == 'en':
            return self.detailed_data['original_body_lines']

        extended_data = self.extended_data
        if 'translated_text' not in extended_data:
            return None
        if 'en' not in extended_data['translated_text']:
            return None
        return extended_data['translated_text']['en']['body_lines']

    @cached_property
    def en_body_lines_shorter(self) -> list[str]:
        MAX_CHARS = 640
        n_total = 0
        lines = []
        for line in self.en_body_lines:
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
        www.download(NewsArticle.TEMP_SUMMARY_PATH, force=True)

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
