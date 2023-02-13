# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IthomeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class IthomeArticleItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    day = scrapy.Field()
    views = scrapy.Field()
    like = scrapy.Field()
    theme_id = scrapy.Field()
    publish_timestamp = scrapy.Field()
    created_timestamp = scrapy.Field()
    updated_timestamp = scrapy.Field()


class IthomeGroupItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    img_url = scrapy.Field()
    created_timestamp = scrapy.Field()
    updated_timestamp = scrapy.Field()


class IthomeThemeItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    group_id = scrapy.Field()
    author = scrapy.Field()
    publish_timestamp = scrapy.Field()
    created_timestamp = scrapy.Field()
    updated_timestamp = scrapy.Field()
