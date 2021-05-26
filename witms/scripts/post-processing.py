import csv
import json
import pathlib
import sys
from argparse import ArgumentParser
from collections import defaultdict
from itertools import zip_longest
from json.decoder import JSONDecodeError
from typing import DefaultDict, Dict, Iterable, Iterator, Tuple, Union

from dateutil.parser import parse
from dateutil.parser._parser import ParserError
from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import BulkIndexError

LINE_BUFFER = 10000


def grouper(iterable: Iterable, n, fillvalue=""):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def get_isotimestamp_and_year(date: str) -> Union[Tuple[str, int], Tuple[None, None]]:
    try:
        parsed = parse(date)
    except ParserError:
        return None, None
    else:
        year = parsed.year
        iso_timestamp = parsed.isoformat()
        return iso_timestamp, year


def filter_items(
    items: Iterator[Union[Dict, None]], filter_period: int
) -> Iterator[Union[Dict, None]]:
    for item in items:
        if filter_period == 0:
            yield item
        if not item:
            continue
        publish_time = item.get("publish_timestamp")
        update_time = item.get("update_timestamp")
        publish_year = None
        update_year = None
        if publish_time is not None:
            publish_timestamp, publish_year = get_isotimestamp_and_year(publish_time)
            item["publish_timestamp"] = publish_timestamp
        if update_time is not None:
            update_timestamp, update_year = get_isotimestamp_and_year(update_time)
            item["update_timestamp"] = update_timestamp
        if publish_time and publish_year and publish_year >= filter_period:
            yield item
        elif not publish_year and (update_year and update_year >= filter_period):
            yield item
        else:
            continue


def build_section_map(section_map_file: str) -> DefaultDict[str, DefaultDict[str, str]]:
    with open(section_map_file) as f:
        section_map = defaultdict(lambda: defaultdict(lambda: "misc"))
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            website = row["Website"].lower()
            website_section = row["Section Name"].lower()
            greater_section = row["General Section"].lower()
            section_map[website][website_section] = greater_section
    return section_map


def map_sections(items: Iterator[Union[Dict, None]], section_map_file: str):
    section_map = build_section_map(section_map_file)
    for item in items:
        website = item["portal"].lower()
        try:
            section = item["section"].lower()
        except KeyError:
            item["section"] = "Misc"
        else:
            greater_section = section_map[website][section]
            item["greater_section"] = greater_section.title()
        yield item


def load_json(lines: Iterator[str]) -> Iterator[Union[Dict, None]]:
    for line in lines:
        try:
            obj = json.loads(line)
        except JSONDecodeError:
            continue
        else:
            yield obj


def process_batch(
    lines: Iterator[str],
    filter_period: int,
    elastic_ingest: bool,
    section_map_file: str,
):
    client = Elasticsearch(hosts="localhost")
    es_items = []
    data_generator = filter_items(load_json(lines), filter_period)
    if section_map_file:
        data_generator = map_sections(data_generator, section_map_file)
    for obj in data_generator:
        if not obj:
            continue
        authors = obj.get("authors")
        if authors:
            try:
                authors = authors.split("|")
            except AttributeError:
                pass
            else:
                obj["authors"] = authors
        es_item = {"_index": "news-index", "_source": obj}
        es_items.append(es_item)
        if not elastic_ingest:
            json.dump(obj, sys.stdout)
            print()
    if elastic_ingest:
        try:
            helpers.bulk(client, es_items)
        except BulkIndexError as e:
            print(e)


def process_file(
    file_path: pathlib.Path,
    filter_period: int,
    elastic_ingest=False,
    section_map_file=None,
) -> None:
    with open(file_path) as f:
        for lines in grouper(f, LINE_BUFFER):
            process_batch(lines, filter_period, elastic_ingest, section_map_file)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("inputfile")
    parser.add_argument("-f", "--filter-period", type=int, default=0)
    parser.add_argument("-e", "--elastic", action="store_true")
    parser.add_argument("-m", "--section-map-file")
    args = parser.parse_args()
    if args.elastic and args.filter_period:
        print(
            f"Processing {args.input_file} and ingesting into news-index...",
            file=sys.stderr,
        )
    elif args.elastic:
        print(f"Ingesting {args.inputfile} into news-index...", file=sys.stderr)
    elif args.filter_period:
        print(f"Processing {args.inputfile}...", file=sys.stderr)
    process_file(
        args.inputfile, args.filter_period, args.elastic, args.section_map_file
    )
    print("Finished!", file=sys.stderr)
