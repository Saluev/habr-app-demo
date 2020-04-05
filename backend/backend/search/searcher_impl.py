from typing import Any, Optional, Iterable, List

from elasticsearch import Elasticsearch

from backend.search.searcher import CardSearchResult, Searcher, TagStats


ElasticsearchQuery = Any


class ElasticsearchSearcher(Searcher):

    TAGS_AGGREGATION_NAME = "tags_aggregation"

    def __init__(self, elasticsearch_client: Elasticsearch, cards_index_name: str):
        self.elasticsearch_client = elasticsearch_client
        self.cards_index_name = cards_index_name

    def search_cards(self, query: str = "", count: int = 20, offset: int = 0,
                     tags: Optional[Iterable[str]] = None) -> CardSearchResult:
        result = self.elasticsearch_client.search(index=self.cards_index_name, body={
            "size": count,
            "from": offset,
            "query": {
                "bool": {
                    "must": self._make_text_queries(query),
                    "filter": self._make_filter_queries(tags),
                }
            },
            "aggregations": {
                self.TAGS_AGGREGATION_NAME: {
                    "terms": {"field": "tags"}
                }
            }
        })
        total_count = result["hits"]["total"]["value"]
        tag_stats = [
            TagStats(tag=bucket["key"], cards_count=bucket["doc_count"])
            for bucket in result["aggregations"][self.TAGS_AGGREGATION_NAME]["buckets"]
        ]
        return CardSearchResult(
            total_count=total_count,
            card_ids=[hit["_id"] for hit in result["hits"]["hits"]],
            next_card_offset=offset + count if offset + count < total_count else None,
            tag_stats=tag_stats,
        )

    def _make_filter_queries(self, tags: Optional[Iterable[str]] = None) -> List[ElasticsearchQuery]:
        return [] if tags is None else [{
            "term": {
                "tags": {
                    "value": tag
                }
            }
        } for tag in tags]

    def _make_text_queries(self, query: str) -> List[ElasticsearchQuery]:
        return [] if not query else [{
            "multi_match": {
                "query": query,
                "fields": ["name^3", "tags.text", "text"],
            }
        }]
