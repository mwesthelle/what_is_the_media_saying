from scrapy import Spider
from scrapy.linkextractors import LinkExtractor
from witms.items import Article
from witms.loaders import ArticleLoader


class RTSpider(Spider):
    name = "rt"
    portal_name = "RT News"
    allowed_domains = ["www.rt.com"]
    start_urls = ["https://www.rt.com/"]
    link_extractor = LinkExtractor()

    def parse(self, response):
        loader = ArticleLoader(item=Article(), response=response)
        loader.add_value("url", response.url)
        loader.add_value("portal", RTSpider.portal_name)
        loader.add_xpath("section", '//meta[@property="article:section"]/@content')
        loader.add_xpath("section", '//meta[@itemprop="articleSection"]/@content')
        loader.add_xpath("authors", '//div[@class="article__author-text"]//strong//text()')
        loader.add_css("title", "h1 *::text")
        loader.add_xpath("title", '//meta[@name="title"]/@content')
        loader.add_xpath("title", '//meta[@property="og:title"]/@content')
        loader.add_xpath("description", '//meta[@name="description"]/@content')
        loader.add_xpath("description", '//meta[@property="og:description"]/@content')
        loader.add_xpath("content", "//article//p//text()")
        loader.add_xpath("content", "//p//text()")
        loader.add_xpath(
            "publish_timestamp", '//meta[@name="published_time_telegram"]/@content'
        )
        loader.add_xpath(
            "publish_timestamp", '//meta[@property="article:published_time"]/@content'
        )
        loader.add_xpath(
            "publish_timestamp", '//time[@itemprop="datePublished"]/@datetime'
        )
        loader.add_xpath(
            "publish_timestamp", '//script//text()', re='"datePublished":\s*"(.*?)"'
        )
        loader.add_xpath(
            "update_timestamp", '//meta[@property="article:modified_time"]/@content'
        )
        loader.add_xpath(
            "update_timestamp", '//time[@itemprop="dateModified"]/@datetime'
        )
        loader.add_xpath(
            "update_timestamp", '//script//text()', re='"dateModified":\s*"(.*?)"'
        )
        yield loader.load_item()

        for link in self.link_extractor.extract_links(response):
            yield response.follow(link.url, callback=self.parse)
