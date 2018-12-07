# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class QunaerPipeline(object):
    def process_item(self, item, spider):
        return item

class QunaerMongoPipeline(object):
    collection = 'qunaer_data'
    def __init__(self, mongo_uri, mongo_db):
         self.mongo_uri = mongo_uri
         self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        '''
        scrapy为我们访问settings提供了这样的一个方法，这里，
        我们需要从settings.py文件中，取得数据库的URI和数据库名称
        '''
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        '''
        爬虫一旦开启，就会实现这个方法，连接到数据库
        '''
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        '''
        爬虫一旦关闭，就会实现这个方法，关闭数据库连接
        '''
        self.client.close()

    def process_item(self, item, spider):
        '''
            每个实现保存的类里面必须都要有这个方法，且名字固定，用来具体实现怎么保存
        '''
        data={
            'province':item['province'],
            'scenic_name':item['scenic_name'],
            'location':item['location'],
            'price':item['price'],
        }
        table = self.db[self.collection]
        table.insert_one(data)
        return item