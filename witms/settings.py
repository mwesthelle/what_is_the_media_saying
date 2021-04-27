BOT_NAME = "witms"

SPIDER_MODULES = ["witms.spiders"]
NEWSPIDER_MODULE = "witms.spiders"

ROBOTSTXT_OBEY = True
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
)

CONCURRENT_REQUESTS = 32

ITEM_PIPELINES = {
    "witms.pipelines.RequiredPropsPipeline": 300,
    "witms.pipelines.OldestPeriodPipeline": 400,
}

FEED_EXPORT_ENCODING = "utf-8"

ES_INDEX_NAME = "news-index"
ES_HOSTS = "localhost"
ES_BUFFER_SIZE = 1000

OLDEST_ALLOWED_PERIOD = 2018
