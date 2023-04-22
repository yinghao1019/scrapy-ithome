# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime, timezone

import pymongo
from scrapy.exceptions import DropItem

from ithome import items as items
from ithome.utils.encrypt_utils import decrypt


# useful for handling different item types with a single interface
class IthomePipeline:
    def process_item(self, item, spider):
        return item


class CleanStringPipeline:
    def process_item(self, item, spider):
        for (field, value) in item.items():
            if type(item.get(field)) is str:
                item[field] = value.strip()
        return item


class DropNullPipeline:
    def process_item(self, item, spider):
        if 'url' in item:
            if item.get('url') is None:
                raise DropItem("item's url is null")
        return item


class AbstractMongoPipeline:
    collection_name = None

    def __init__(self, host, mongo_db, username, password):
        self.mongo_uri = f'mongodb://{username}:{decrypt(password)}@{host}:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@ithome@'
        self.client = pymongo.MongoClient(self.mongo_uri, port=10255)
        self.db = self.client[mongo_db]
        self.collection = self.db[self.collection_name]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MONGO_HOST'),
            mongo_db=crawler.settings.get('MONGO_DATABASE'),
            username=crawler.settings.get('MONGO_USERNAME'),
            password=crawler.settings.get('MONGO_PASSWORD')
        )

    def close_spider(self, spider):
        self.client.close()


class IronmanThemeMongoPipeline(AbstractMongoPipeline):
    collection_name = 'theme'

    def process_item(self, item, spider):
        now = datetime.now(timezone.utc)
        if isinstance(item, items.IronmanThemeItem):
            document = self.collection.find_one({'url': item['url']})
            group_id = item.pop('group_id')
            data = dict(item)

            if not document:
                data['created_timestamp'] = now
                data['updated_timestamp'] = now

                insert_result = self.collection.insert_one(data)
                item['_id'] = insert_result.inserted_id
                self.insert_group(insert_result.inserted_id, group_id)
            else:
                data['updated_timestamp'] = now
                self.collection.update_one(
                    {'_id': document['_id']},
                    {'$set': data},
                    upsert=True
                )
                item['_id'] = document['_id']
        return item

    def insert_group(self, theme_id, group_id):
        if group_id:
            document = self.db['category'].find_one({'_id': group_id})
            themes = document.get('themes', [])
            themes.append(theme_id)
            self.db['category'].update_one({'_id': document['_id']}, {'$set': {"themes": themes}})


class IthomeGroupMongoPipeline(AbstractMongoPipeline):
    collection_name = 'category'

    def process_item(self, item, spider):
        now = datetime.now(timezone.utc)
        if isinstance(item, items.IthomeGroupItem):
            document = self.collection.find_one({'name': item['name']})
            data = dict(item)

            if not document:
                data['created_timestamp'] = now
                data['updated_timestamp'] = now
                insert_result = self.collection.insert_one(data)
                item['_id'] = insert_result.inserted_id
            else:
                data['updated_timestamp'] = now
                self.collection.update_one(
                    {'_id': document['_id']},
                    {'$set': data},
                    upsert=True
                )
                item['_id'] = document['_id']

        return item


class IronmanArticleMongoPipeline(AbstractMongoPipeline):
    collection_name = 'article'

    def process_item(self, item, spider):
        now = datetime.now(timezone.utc)
        if isinstance(item, items.IronmanArticleItem):
            document = self.collection.find_one({'url': item['url']})
            theme_id = item.pop('theme_id')
            data = dict(item)

            if not document:
                data['created_timestamp'] = now
                data['updated_timestamp'] = now

                insert_result = self.collection.insert_one(data)
                item['_id'] = insert_result.inserted_id
                self.insert_theme(theme_id, insert_result.inserted_id)
            else:
                data['updated_timestamp'] = now
                self.collection.update_one(
                    {'_id': document['_id']},
                    {'$set': data},
                    upsert=True
                )
                item['_id'] = document['_id']
        return item

    def insert_theme(self, theme_id, article_id):
        theme_collection = self.db['theme']
        document = theme_collection.find_one({'_id': theme_id})
        articles = document.get('articles', [])
        articles.append(article_id)

        theme_collection.update_one({'_id': document['_id']}, {'$set': {"articles": articles}})
