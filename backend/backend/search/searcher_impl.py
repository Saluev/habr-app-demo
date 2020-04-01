from typing import Any

from elasticsearch import Elasticsearch

from backend.search.searcher import CardSearchResult, Searcher


ElasticsearchQuery = Any


class ElasticsearchSearcher(Searcher):

    def __init__(self, elasticsearch_client: Elasticsearch, cards_index_name: str):
        self.elasticsearch_client = elasticsearch_client
        self.cards_index_name = cards_index_name

    def search_cards(self, query: str = "", count: int = 20, offset: int = 0) -> CardSearchResult:
        result = self.elasticsearch_client.search(index=self.cards_index_name, body={
            "size": count,
            "from": offset,
            "query": self._make_text_query(query) if query else self._match_all_query
        })
        total_count = result["hits"]["total"]["value"]
        return CardSearchResult(
            total_count=total_count,
            card_ids=[hit["_id"] for hit in result["hits"]["hits"]],
            next_card_offset=offset + count if offset + count < total_count else None,
        )

    def _make_text_query(self, query: str) -> ElasticsearchQuery:
        return {
            "multi_match": {
                "query": query,
                "fields": ["name^3", "tags.text", "text"],
            }
        }

    _match_all_query: ElasticsearchQuery = {"match_all": {}}
