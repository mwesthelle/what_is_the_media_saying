from scrapy import Spider
from scrapy.linkextractors import LinkExtractor
from witms.items import Article
from witms.loaders import ArticleLoader


class HuffPostSpider(Spider):
    name = "huffpost"
    portal_name = "HuffPost"
    allowed_domains = ["www.huffpost.com"]
    start_urls = ["https://www.huffpost.com/"]
    link_extractor = LinkExtractor(allow="/entry/")

    def parse(self, response):
        loader = ArticleLoader(item=Article(), response=response)
        loader.add_value("url", response.url)
        loader.add_value("portal", HuffPostSpider.portal_name)
        loader.add_xpath("section", '//meta[@name="article:section"]/@content')
        loader.add_xpath("section", '//meta[@property="article:section"]/@content')
        loader.add_xpath("section", '//meta[@itemprop="articleSection"]/@content')
        loader.add_css("authors", "a[class*=-author-name] *::text")
        loader.add_css("title", "h1 *::text")
        loader.add_xpath("title", '//meta[@name="title"]/@content')
        loader.add_xpath("title", '//meta[@property="og:title"]/@content')
        loader.add_xpath("description", '//meta[@name="description"]/@content')
        loader.add_xpath("description", '//meta[@property="og:description"]/@content')
        loader.add_css("content", "section[id=entry-body] *::text")
        loader.add_xpath("content", "//article//p//text()")
        loader.add_xpath("content", "//p//text()")
        loader.add_xpath(
            "publish_timestamp", '//meta[@property="article:published_time"]/@content'
        )
        loader.add_xpath(
            "publish_timestamp", '//time[@itemprop="datePublished"]/@datetime'
        )
        loader.add_xpath(
            "publish_timestamp", "//script//text()", re=r'"datePublished":\s*"(.*?)"'
        )
        loader.add_xpath(
            "update_timestamp", '//meta[@property="article:modified_time"]/@content'
        )
        loader.add_xpath(
            "update_timestamp", '//time[@itemprop="dateModified"]/@datetime'
        )
        loader.add_xpath(
            "update_timestamp", "//script//text()", re=r'"dateModified":\s*"(.*?)"'
        )
        yield loader.load_item()

        for link in self.link_extractor.extract_links(response):
            yield response.follow(link.url, callback=self.parse)
