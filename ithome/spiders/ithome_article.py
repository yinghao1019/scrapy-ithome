from abc import ABC
from typing import Iterable

import pymongo
import scrapy
from scrapy.http import Response

from ithome.items import IthomeArticleItem
from ithome.utils.date_utils import to_datetime
from ithome.utils.string_utils import parse_int


class IthomeArticleSpider(scrapy.Spider, ABC):
    name = 'ithome_article'
    allowed_domains = ['ithome.com.tw']

    def __init__(self, mongo_uri=None, mongo_db=None, *args, **kwargs):
        super(IthomeArticleSpider, self).__init__(*args, **kwargs)
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]

    def start_requests(self) -> Iterable:
        theme_documents = self.db['theme'].find({"articles": {"$exists": False}}).limit(3)
        for doc in theme_documents:
            if 'url' in doc:
                yield scrapy.Request(doc['url'], callback=self.parse_page, cb_kwargs=dict(theme_id=doc['_id']))
        self.client.close()

    def parse_page(self, response: Response, theme_id: int) -> Iterable:
        next_page = response.css("ul.pagination:last-child>a[href]")
        articles = response.css("div.ir-profile-content").css("div.qa-list")
        # 提取當前頁面的文章清單
        for article in articles:
            article_item = IthomeArticleItem()
            info = article.css("div.profile-list__condition")
            like = info.css("div a.qa-condition:first-child > span.qa-condition__count::text").get()
            views = info.css("div a.qa-condition:last-child > span.qa-condition__count::text").get()

            content = article.css("div.profile-list__content")
            title = content.css("h3.qa-list__title a")
            publish_timestamp = content.css("div.qa-list__info > a[title]::attr(title)").get()
            day_str = content.css("span.ir-qa-list__days::text").get().strip()

            article_item['theme_id'] = theme_id
            article_item['like'] = int(like) if (like is not None and like.isdigit()) else like
            article_item['views'] = int(views) if (views is not None and views.isdigit()) else views
            article_item['title'] = title.css("a::text").get()
            article_item['url'] = title.css("a::attr(href)").get()
            article_item['day'] = parse_int(day_str)
            article_item['description'] = content.css("p.qa-list__desc::text").get().replace("\n", "")
            article_item['publish_timestamp'] = to_datetime(publish_timestamp)

            yield article_item
        # 爬取下一頁的主題文章清單
        if next_page:
            next_page_url = next_page.css("a[rel='next']::attr(href)").get()
            yield scrapy.Request(next_page_url, callback=self.parse_page, cb_kwargs=dict(theme_id=theme_id))
