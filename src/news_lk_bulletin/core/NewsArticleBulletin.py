from functools import cached_property

from news_lk_bulletin.core.NewsArticle import NewsArticle


class NewsArticleBulletin:
    def __init__(self, limit: int = 10):
        self.limit = limit

    @cached_property
    def blurb(self) -> str:
        news_article_list = NewsArticle.list_all()
        en_news_article_list = [
            news_article
            for news_article in news_article_list
            if news_article.original_lang == 'en'
        ]
        recent_news_article_list = en_news_article_list[: self.limit]
        lines = ['...']
        for news_article in recent_news_article_list:
            lines.append('# ' + news_article.original_title)
            lines.append(f'*{news_article.time_str}*')
            lines.append(f'[{news_article.newspaper_id}]({news_article.url})')
            lines.extend(news_article.original_body_lines)
            lines.append('...')
        return '\n\n'.join(lines)
