from scrapy import Spider
from scrapy.linkextractors import LinkExtractor
from witms.items import Article
from witms.loaders import ArticleLoader


class FoxNewsSpider(Spider):
    name = "foxnews"
    portal_name = "Fox News"
    allowed_domains = ["foxnews.com"]
    start_urls = ["https://www.foxnews.com"]
    link_extractor = LinkExtractor(
        deny=["/v/", "/person/", "/category/", "video.foxnews.com"]
    )

    def parse(self, response):
        loader = ArticleLoader(item=Article(), response=response)
        loader.add_value("url", response.url)
        loader.add_value("portal", FoxNewsSpider.portal_name)
        loader.add_xpath("section", '//meta[@name="prism.section"]/@content')
        loader.add_xpath("section", '//meta[@name="article:section"]/@content')
        loader.add_xpath("section", '//meta[@property="article:section"]/@content')
        loader.add_xpath("section", '//meta[@itemprop="articleSection"]/@content')
        # URL must contain "/person/?/"", where "?" is any one lowercase letter
        loader.add_xpath(
            "authors",
            r'//div[contains(@class, "author")]'
            + r'//a[re:test(@href, "\/person\/[a-z]\/")]//text()',
        )
        loader.add_xpath("authors", '//meta[@name="author"]/@content')
        loader.add_xpath("authors", '//a[@rel="author"]//text()')
        loader.add_css("title", "h1 *::text")
        loader.add_xpath("title", '//meta[@name="title"]/@content')
        loader.add_xpath("title", '//meta[@property="og:title"]/@content')
        loader.add_xpath("description", '//meta[@name="description"]/@content')
        loader.add_xpath("description", '//meta[@property="og:description"]/@content')
        loader.add_css("content", "div[class*=article-body] *::text")
        loader.add_xpath("content", "//article//p//text()")
        loader.add_xpath("content", "//p//text()")
        loader.add_xpath(
            "publish_timestamp", '//meta[@name="dcterms.created"]/@content'
        )
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
            "update_timestamp", '//meta[@name="dcterms.modified"]/@content'
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
