BOT_NAME = "witms"

SPIDER_MODULES = ["witms.spiders"]
NEWSPIDER_MODULE = "witms.spiders"

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 32

ITEM_PIPELINES = {
    "witms.pipelines.ElasticSearchPipeline": 300,
}
