# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch, helpers

BUFFER_SIZE = 1000


class ElasticSearchPipeline:
    def __init__(self):
        self.items_buffer = []

    def open_spider(self, spider):
        self.client = Elasticsearch(hosts=["localhost"])

    def process_item(self, item, spider):
        action = {"_index": "news-index", "_source": dict(item)}
        self.items_buffer.append(action)
        if len(self.items_buffer) >= BUFFER_SIZE:
            helpers.bulk(self.client, self.items_buffer)
            self.items_buffer = []
        return item
