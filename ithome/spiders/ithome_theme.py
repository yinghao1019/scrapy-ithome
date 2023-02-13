from typing import Iterable, Tuple

import pymongo
import scrapy
from scrapy import Item, selector
from scrapy.exceptions import CloseSpider
from scrapy.http import Response
from scrapy.utils.project import get_project_settings

from ithome.items import IthomeGroupItem, IthomeThemeItem
from ithome.utils.encrypt_utils import decrypt


class IthomeThemeSpider(scrapy.Spider):
    name = 'ithome_theme'
    allowed_domains = ['ithome.com.tw']

    def __init__(self, crawl_pages=5, *args, **kwargs):
        super(IthomeThemeSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        host = settings.get('MONGO_HOST')
        username = settings.get('MONGO_USERNAME')
        password = decrypt(settings.get('MONGO_PASSWORD'))

        self.client = pymongo.MongoClient(f'mongodb+srv://{username}:{password}@{host}/?retryWrites=true&w=majority')
        self.db = self.client[settings.get('MONGO_DATABASE')]
        self.crawl_pages = crawl_pages

    def start_requests(self) -> Iterable:
        link, start_page = self.get_url()

        for page_num in range(start_page, start_page + self.crawl_pages):
            crawl_url = f"{link}&page={page_num}"
            self.logger.info(f"crawl link:{crawl_url},page_index:{page_num}")

            yield scrapy.Request(crawl_url, callback=self.parse)

    def parse(self, response: Response) -> Iterable:
        themes = response.css('div.contestants-wrapper').css('div.contestants-list')

        if (len(themes) > 0):
            for theme in themes:
                theme_group = IthomeGroupItem()
                group_tag = theme.css('div.contestants-list__group')
                theme_group['name'] = group_tag.css('div div::text').get()
                theme_group['img_url'] = group_tag.css('img::attr(src)').get()

                yield theme_group
                if '_id' in theme_group:
                    yield from self.parse_theme(theme_group['_id'], theme)
        else:
            raise CloseSpider(
                f"Not element can't crawl with url:{response.url}")

    def parse_theme(self, group_id: int, theme: selector) -> Item:

        title = theme.css('a.contestants-list__title')
        theme_item = IthomeThemeItem()
        theme_item['title'] = title.css('::text').get()
        theme_item['url'] = title.css('::attr(href)').get()
        theme_item['description'] = theme.css('p.contestants-list__desc::text').get()
        theme_item['group_id'] = group_id
        theme_item['author'] = theme.css('div.contestants-list__name::text').get()

        yield theme_item

    def get_url(self) -> Tuple[str, str]:
        collection = self.db["crawl_source"]
        document = collection.find({"$expr": {"$gt": ["$max_page", "$start_page"]}}).sort("annual",
                                                                                          pymongo.ASCENDING).limit(1)
        document = next(document)
        start_page = document.get("start_page")
        max_page = document.get("max_page")
        url = document.get("url")
        # 更新可爬取的頁數
        left_page = max_page - (start_page + self.crawl_pages)
        if left_page < 0:
            self.crawl_pages = self.crawl_pages + left_page

        # 更新document
        document["start_page"] = start_page + self.crawl_pages
        collection.update_one({'_id': document['_id']},
                              {'$set': document})
        self.client.close()

        return url, start_page
