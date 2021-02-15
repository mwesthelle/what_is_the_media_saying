from scrapy import Request, Spider
from witms.items import Article
from witms.loaders import ArticleLoader


class GuardianSpider(Spider):
    name = "Guardian"
    allowed_domains = ["theguardian.com"]
    start_urls = ["http://www.theguardian.com/international"]

    @staticmethod
    def get_news_article(response):
        loader = ArticleLoader(item=Article(), response=response)
        loader.add_value("url", response.url)
        loader.add_value("portal", GuardianSpider.name)
        loader.add_xpath("section", "//meta[@property=\"article:section\"]/@content")
        loader.add_xpath("authors", "//meta[@name=\"author\"]/@content")
        loader.add_css("title", "h1 *::text")
        loader.add_xpath("title", "//meta[@name=\"title\"]/@content")
        loader.add_xpath("title", "//meta[@property=\"og:title\"]/@content")
        loader.add_xpath("description", "//meta[@name=\"description\"]/@content")
        loader.add_xpath("description", "//meta[@property=\"og:description\"]/@content")
        loader.add_css("content", "p *::text") # TODO: fix me
        loader.add_xpath("publish_timestamp", "//meta[@property=\"article:published_time\"]/@content")
        loader.add_xpath("publish_timestamp", "//time[@itemprop=\"datePublished\"]/@datetime")
        loader.add_xpath("update_timestamp", "//meta[@property=\"article:modified_time\"]/@content")
        loader.add_xpath("update_timestamp", "//time[@itemprop=\"dateModified\"]/@datetime")
        yield loader.load_item()

    def parse(self, response):
        for article in response.css("a[data-link-name*=article]::attr(href)").extract():
            yield Request(url=article, callback=self.get_news_article)
