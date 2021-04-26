import json
import pathlib
import sys
from argparse import ArgumentParser
from itertools import zip_longest
from json.decoder import JSONDecodeError
from typing import Dict, Iterable, Iterator, Union

from dateutil.parser import parse
from dateutil.parser._parser import ParserError
from elasticsearch import Elasticsearch, helpers

LINE_BUFFER = 10000


def grouper(iterable: Iterable, n, fillvalue=""):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def filter_items(
    items: Iterator[Union[Dict, None]], filter_period: int
) -> Iterator[Union[Dict, None]]:
    for item in items:
        if not item:
            continue
        publish_time = item.get("publish_timestamp")
        update_time = item.get("update_timestamp")
        publish_year = None
        update_year = None
        if publish_time is not None:
            try:
                publish_year = parse(publish_time).year
            except ParserError:
                pass
        if update_time is not None:
            try:
                update_year = parse(update_time).year
            except ParserError:
                pass
        if publish_year and publish_year >= filter_period:
            yield item
        elif update_year and update_year >= filter_period:
            yield item
        else:
            continue


def load_json(lines: Iterator[str]) -> Iterator[Union[Dict, None]]:
    for line in lines:
        try:
            obj = json.loads(line)
        except JSONDecodeError:
            continue
        else:
            yield obj


def process_file(
    file_path: pathlib.Path, filter_period: int, elastic_ingest=False
) -> None:
    client = Elasticsearch(hosts="localhost")
    with open(file_path) as f:
        for lines in grouper(f, LINE_BUFFER):
            es_items = []
            for obj in filter_items(load_json(lines), filter_period):
                if not obj:
                    continue
                es_item = {"_index": "news-index", "_source": obj}
                es_items.append(es_item)
                if not elastic_ingest:
                    json.dump(obj, sys.stdout)
                    print()
            if elastic_ingest:
                helpers.bulk(client, es_items)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("inputfile")
    parser.add_argument("-f", "--filter-period", type=int, default=0)
    parser.add_argument("-e", "--elastic", action="store_true")
    args = parser.parse_args()
    process_file(args.inputfile, args.filter_period, args.elastic)
