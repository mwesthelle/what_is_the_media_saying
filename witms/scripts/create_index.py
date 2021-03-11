from argparse import ArgumentParser
import json

from elasticsearch import Elasticsearch


def create_index(es_client: Elasticsearch, settings_path: str, index_name: str) -> None:
    with open(settings_path) as sf:
        settings = json.load(sf)
        es_client.indices.create(index=index_name, body=settings)


if __name__ == "__main__":
    parser = ArgumentParser("Helper script to create an ElasticSearch index")
    parser.add_argument(
        "--host",
        help="The ElasticSearch host on which we wish to create an index",
        default="localhost",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="The port on which the Elasticsearch host is listening",
        default=9200,
    )
    parser.add_argument(
        "-n",
        "--index-name",
        help="The name of the ElasticSearch index you wish to create",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--settings-file",
        help="A JSON file containing the index settings and mappings",
        required=True,
    )
    args = parser.parse_args()
    es_client = Elasticsearch(args.host, port=args.port)
    create_index(es_client, args.settings_file, args.index_name)
