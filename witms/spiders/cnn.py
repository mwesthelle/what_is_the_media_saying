from scrapy import Spider
from scrapy.linkextractors import LinkExtractor
from witms.items import Article
from witms.loaders import ArticleLoader


class CnnSpider(Spider):
    name = "cnn"
    portal_name = "CNN"
    allowed_domains = ["edition.cnn.com"]
    start_urls = ["https://edition.cnn.com"]
    link_extractor = LinkExtractor(deny=["/videos/", "/profiles/"])

    def parse(self, response):
        loader = ArticleLoader(item=Article(), response=response)
        loader.add_value("url", response.url)
        loader.add_value("portal", CnnSpider.portal_name)
        loader.add_xpath("section", '//meta[@name="section"]/@content')
        loader.add_xpath("section", '//meta[@property="article:section"]/@content')
        loader.add_xpath("section", '//meta[@itemprop="articleSection"]/@content')
        loader.add_css("authors", "a[href*=\/profiles\/] *::text")
        loader.add_css("title", "h1 *::text")
        loader.add_xpath("title", '//meta[@name="title"]/@content')
        loader.add_xpath("title", '//meta[@property="og:title"]/@content')
        loader.add_xpath("description", '//meta[@name="description"]/@content')
        loader.add_xpath("description", '//meta[@property="og:description"]/@content')
        loader.add_css("content", "article div[class*=zn-body__paragraph] *::text")
        loader.add_css("content", "div[class*=Article__body] *::text")
        loader.add_css("content", "div[class*=BasicArticle__main] *::text")
        loader.add_css("content", "div[class=story] *::text")
        loader.add_xpath("content", "//article//p//text()")
        loader.add_xpath("content", "//p//text()")
        loader.add_xpath("publish_timestamp", '//meta[@name="pubdate"]/@content')
        loader.add_xpath("publish_timestamp", '//meta[@property="og:pubdate"]/@content')
        loader.add_xpath(
            "publish_timestamp", '//meta[@property="article:published_time"]/@content'
        )
        loader.add_xpath(
            "publish_timestamp", '//time[@itemprop="datePublished"]/@datetime'
        )
        loader.add_xpath("update_timestamp", '//meta[@name="lastmod"]/@content')
        loader.add_xpath(
            "update_timestamp", '//meta[@property="article:modified_time"]/@content'
        )
        loader.add_xpath(
            "update_timestamp", '//time[@itemprop="dateModified"]/@datetime'
        )
        yield loader.load_item()

        for link in self.link_extractor.extract_links(response):
            yield response.follow(link.url, callback=self.parse)
