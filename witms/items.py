# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

from witms.utils.text_cleaning import parse_timestamp, replace_smart_quotes


class Article(scrapy.Item):
    author = scrapy.Field()
    article_text = scrapy.Field(output_processor=MapCompose(replace_smart_quotes))
    paper_section = scrapy.Field()
    timestamp = scrapy.Field(
        input_processor=MapCompose(parse_timestamp), output_processor=TakeFirst()
    )
