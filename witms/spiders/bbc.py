from scrapy import Request, Spider
from scrapy.linkextractors import LinkExtractor
from witms.items import Article
from witms.loaders import ArticleLoader


class BbcSpider(Spider):
    name = "bbc"
    portal_name = "BBC"
    allowed_domains = ["bbc.com", "bbc.co.uk"]
    start_urls = ["https://www.bbc.com/news"]
    link_extractor = LinkExtractor(allow="/news/")

    @staticmethod
    def get_news_article(response):
        loader = ArticleLoader(item=Article(), response=response)
        loader.add_value("url", response.url)
        loader.add_value("portal", BbcSpider.portal_name)
        loader.add_xpath("section", '//meta[@property="article:section"]/@content')
        loader.add_css("authors", "a[class*=-ContributorLink] *::text")
        loader.add_css("title", "h1 *::text")
        loader.add_xpath("title", '//meta[@name="title"]/@content')
        loader.add_xpath("title", '//meta[@property="og:title"]/@content')
        loader.add_xpath("description", '//meta[@name="description"]/@content')
        loader.add_xpath("description", '//meta[@property="og:description"]/@content')
        loader.add_xpath("content", "//article//p//text()")
        # No publish_timestamp here
        loader.add_xpath(
            "update_timestamp", '//meta[@property="article:modified_time"]/@content'
        )
        loader.add_xpath(
            "update_timestamp", '//time[@itemprop="dateModified"]/@datetime'
        )
        loader.add_xpath("update_timestamp", "//time/@datetime")
        yield loader.load_item()

    def parse(self, response):
        for link in self.link_extractor.extract_links(response):
            yield Request(link.url, callback=self.get_news_article)
