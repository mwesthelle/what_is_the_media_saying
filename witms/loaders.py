from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join


def replace_smart_quotes(text):
    return (
        text.replace(u"\u2018", "'")
        .replace(u"\u2019", "'")
        .replace(u"\u201c", '"')
        .replace(u"\u201d", '"')
    )


class ArticleLoader(ItemLoader):
    default_output_processor = TakeFirst()

    authors_in = Join("|")
    title_in = Join(separator='')
    content_in = MapCompose(replace_smart_quotes)

    content_out = Join()
