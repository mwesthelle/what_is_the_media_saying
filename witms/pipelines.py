# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch, helpers
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class RequiredPropsPipeline:
    def process_item(self, item, spider):
        # We need to check if an item has any of a few properties in order to check
        # whether the item is really a news article
        adapter = ItemAdapter(item)
        timestamp_props = {"publish_timestamp", "update_timestamp"}
        has_req_time_prop = any([adapter.get(prop) for prop in timestamp_props])
        if not has_req_time_prop:
            raise DropItem("Article doesn't have the required properties")
        return item


class ElasticSearchPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        index_name = settings.get("ES_INDEX_NAME")
        es_hosts = settings.get("ES_HOSTS")
        es_buffer_size = settings.get("ES_BUFFER_SIZE")
        return cls(index_name, es_hosts, es_buffer_size)

    def __init__(self, es_index, es_hosts="localhost", buffer_size=500):
        self.items_buffer = []
        self.es_index = es_index
        self.buffer_size = buffer_size
        self.es_hosts = [host.strip() for host in es_hosts.split(",")]

    def open_spider(self, spider):
        self.client = Elasticsearch(hosts=self.es_hosts)

    def close_spider(self, spider):
        if len(self.items_buffer) > 0:
            helpers.bulk(self.client, self.items_buffer)
            self.items_buffer = []

    def process_item(self, item, spider):
        es_item = dict(item)
        action = {"_index": self.es_index, "_source": es_item}
        self.items_buffer.append(action)
        if len(self.items_buffer) >= self.buffer_size:
            helpers.bulk(self.client, self.items_buffer)
            self.items_buffer = []
        return item
