# running:
# scrapy runspider g1.py -O output.json

import scrapy
import re
from scrapy.linkextractors import LinkExtractor


class Spider(scrapy.Spider):
    name = 'g1-bot'
    allowed_domains = ['g1.globo.com']
    start_urls = ['https://g1.globo.com/']
    link_extractor = LinkExtractor(allow=['\/noticia\/', '\.ghtml$'])

    def parse(self, response):
        # If this is an article, get data from it
        if response.xpath('//article') is not None:
            yield {
                'bot_name': self.name,
                'url': response.url,
                'title': response.xpath('//meta[@name="title"]/@content').get(),
                'description': response.xpath('//meta[@name="description"]/@content').get(),
                'content': ''.join(response.xpath('//article').xpath('.//*/text()').getall()),
                'date': response.xpath('//time[@itemprop="datePublished"]/@datetime').get(),
                'author': response.xpath('//p[@class="content-publication-data__from"]/@title').get(),
            }

        # Follow more news links
        for link in self.link_extractor.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse)
