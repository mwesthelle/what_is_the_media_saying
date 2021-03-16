BOT_NAME = "witms"

SPIDER_MODULES = ["witms.spiders"]
NEWSPIDER_MODULE = "witms.spiders"

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 32

ITEM_PIPELINES = {
    "witms.pipelines.ElasticSearchPipeline": 300,
}

ES_INDEX_NAME = "news-index"
ES_HOSTS = "localhost"
ES_BUFFER_SIZE = 1000
