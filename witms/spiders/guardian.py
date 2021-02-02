from scrapy import Request, Spider
from scrapy.loader import ItemLoader

from witms.items import Article


class GuardianSpider(Spider):
    name = "guardian"
    allowed_domains = ["theguardian.com"]
    start_urls = ["http://www.theguardian.com/international"]

    @staticmethod
    def get_news_article(response):
        loader = ItemLoader(item=Article(), response=response)
        loader.add_css("author", "a[rel=author] *::text")
        loader.add_css("article_text", "p *::text")
        # URL looks like http://www.theguardian.com/world/blablabla
        section = response.url.split("/")[3]
        loader.add_value("paper_section", section)
        loader.add_css("timestamp", "label[for=dateToggle] ::text")
        loader.add_xpath("timestamp", "//time/@data-timestamp")
        yield loader.load_item()

    def parse(self, response):
        for article in response.css("a[data-link-name*=article]::attr(href)").extract():
            yield Request(url=article, callback=self.get_news_article)
