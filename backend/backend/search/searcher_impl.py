from typing import Any, Optional, Iterable, List

from elasticsearch import Elasticsearch

from backend.search.ranking import SearchRankingManager
from backend.search.searcher import CardSearchResult, Searcher, TagStats


ElasticsearchQuery = Any


class ElasticsearchSearcher(Searcher):

    TAGS_AGGREGATION_NAME = "tags_aggregation"

    def __init__(self, elasticsearch_client: Elasticsearch, ranking_manager: SearchRankingManager,
                 cards_index_name: str):
        self.elasticsearch_client = elasticsearch_client
        self.ranking_manager = ranking_manager
        self.cards_index_name = cards_index_name

    def search_cards(self, query: str = "", count: int = 20, offset: int = 0,
                     tags: Optional[Iterable[str]] = None, ids: Optional[Iterable[str]] = None,
                     enable_rescoring=True) -> CardSearchResult:
        rescoring = {
            "rescore": {
                "window_size": 1000,
                "query": {
                    "rescore_query": {
                        "sltr": {
                            "params": {
                                "query": query
                            },
                            "model": self.ranking_manager.get_current_model_name()
                        }
                    }
                }
            }
        } if enable_rescoring else {}
        result = self.elasticsearch_client.search(index=self.cards_index_name, body={
            "size": count,
            "from": offset,
            "query": {
                "bool": {
                    "must": self._make_text_queries(query),
                    "filter": list(self._make_filter_queries(tags, ids)),
                }
            },
            **rescoring,
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

    def _make_filter_queries(self, tags: Optional[Iterable[str]] = None,
                             ids: Optional[Iterable[str]] = None) -> Iterable[ElasticsearchQuery]:
        if tags is not None:
            for tag in tags:
                yield {
                    "term": {
                        "tags": {
                            "value": tag
                        }
                    }
                }
        if ids is not None:
            yield {
                "terms": {
                    "id": list(ids)
                }
            }

    def _make_text_queries(self, query: str) -> List[ElasticsearchQuery]:
        return [] if not query else [{
            "multi_match": {
                "query": query,
                "fields": ["name^3", "tags.text", "text"],
            }
        }]
