import scrapy


class Article(scrapy.Item):
    url = scrapy.Field()
    portal = scrapy.Field()
    section = scrapy.Field()
    authors = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    content = scrapy.Field()
    publish_timestamp = scrapy.Field()
    update_timestamp = scrapy.Field()
