from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join, Compose


def replace_smart_quotes(text):
    return (
        text.replace(u"\u2018", "'")
        .replace(u"\u2019", "'")
        .replace(u"\u201c", '"')
        .replace(u"\u201d", '"')
    )

def unique(items):
    return list(set(items))


class ArticleLoader(ItemLoader):
    default_output_processor = TakeFirst()

    # ["Alfred ", "Alfred", "John"] -> ["Alfred", "Alfred", "John"]
    authors_in = MapCompose(str.strip)

    # ["Alfred", "Alfred", "John"] -> "Alfred|John"
    authors_out = Compose(unique, Join("|"))

    # ["This is", " Jane\u2019s title "] -> "This is Jane's title"
    title_in = Compose(Join(separator=''), str.strip, replace_smart_quotes)

    # ["This is", " Jane\u2019s description "] -> "This is Jane's description"
    description_in = Compose(Join(separator=''), str.strip, replace_smart_quotes)

    # ["Today is", " a \u201cgood\u201d day"] -> "Today is a \"good\" day"
    content_out = Compose(Join(), replace_smart_quotes)
