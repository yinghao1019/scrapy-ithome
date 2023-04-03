from typing import Iterable

import scrapy
from bson import json_util
from scrapy.http import Response

from ithome.items import IronmanArticleItem
from ithome.utils.date_utils import to_datetime
from ithome.utils.string_utils import parse_int


class IronmanArticleSpider(scrapy.Spider):
    name = 'ironman_article'
    allowed_domains = ['ithome.com.tw']

    def __init__(self, ironman_themes: str, *args, **kwargs):
        super(IronmanArticleSpider, self).__init__(*args, **kwargs)
        self.ironman_themes = json_util.loads(ironman_themes)

    def start_requests(self) -> Iterable:
        for theme in self.ironman_themes:
            if 'theme_url' in theme:
                yield scrapy.Request(theme['theme_url'], callback=self.parse_page,
                                     cb_kwargs=dict(theme_id=theme['theme_id']))

    def parse_page(self, response: Response, theme_id: int) -> Iterable:
        # 提取當前頁面的文章清單
        articles = response.css("div.ir-profile-content").css("div.qa-list")
        for article in articles:
            # parse
            info = article.css("div.profile-list__condition")
            like = info.css("div a.qa-condition:first-child > span.qa-condition__count::text").get()
            views = info.css("div a.qa-condition:last-child > span.qa-condition__count::text").get()

            content = article.css("div.profile-list__content")
            title = content.css("h3.qa-list__title a")
            publish_timestamp = content.css("div.qa-list__info > a[title]::attr(title)").get()
            day_str = content.css("span.ir-qa-list__days, span.ir-qa-list__days--profile::text", ).get()
            # map
            article_item = IronmanArticleItem()
            article_item['theme_id'] = theme_id
            article_item['like'] = int(like) if (like is not None and like.isdigit()) else like
            article_item['views'] = int(views) if (views is not None and views.isdigit()) else views
            article_item['title'] = title.css("a::text").get()
            article_item['url'] = title.css("a::attr(href)").get()
            article_item['description'] = content.css("p.qa-list__desc::text").get().replace("\n", "")
            article_item['publish_timestamp'] = to_datetime(publish_timestamp)
            # additional article
            if day_str is not None:
                article_item['day'] = parse_int(day_str)
            yield article_item

        # 爬取下一頁的文章
        next_page_href = response.css("ul.pagination > li:last-child a[href]")
        if next_page_href:
            next_page_url = next_page_href.attrib['href']
            yield scrapy.Request(next_page_url, callback=self.parse_page, cb_kwargs=dict(theme_id=theme_id))
