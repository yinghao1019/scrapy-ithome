from typing import Iterable, Tuple

import pymongo
import scrapy
from scrapy import Item, selector
from scrapy.exceptions import CloseSpider
from scrapy.http import Response
from scrapy.utils.project import get_project_settings

from ithome.items import IthomeGroupItem, IthomeThemeItem
from ithome.utils.date_utils import extract_datetime, to_datetime, get_year


class IthomeThemeSpider(scrapy.Spider):
    name = 'ithome_theme'
    allowed_domains = ['ithome.com.tw']

    def __init__(self, start_url: str, start_page: str, crawl_pages:str, *args, **kwargs):
        super(IthomeThemeSpider, self).__init__(*args, **kwargs)
        self.start_url = start_url
        self.end_page = int(start_page) + int(crawl_pages)
        self.start_page = int(start_page)

    def start_requests(self) -> Iterable:

        for page_num in range(self.start_page, self.end_page):
            crawl_url = f"{self.start_url}&page={page_num}"
            self.logger.info(f"crawl link:{crawl_url} ")

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
        print(theme.css('div.contestants-list__date::text').get())
        publish_timestamp = extract_datetime(theme.css('div.contestants-list__date::text').get().strip())
        publish_timestamp = to_datetime(publish_timestamp)

        title = theme.css('a.contestants-list__title')
        theme_item = IthomeThemeItem()
        theme_item['title'] = title.css('::text').get()
        theme_item['url'] = title.css('::attr(href)').get()
        theme_item['description'] = theme.css('p.contestants-list__desc::text').get()
        theme_item['group_id'] = group_id
        theme_item['author'] = theme.css('div.contestants-list__name::text').get()
        theme_item['publish_timestamp'] = publish_timestamp
        theme_item['serial_annual'] = get_year(publish_timestamp)

        yield theme_item
