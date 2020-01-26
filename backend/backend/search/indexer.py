import datetime

from elasticsearch import Elasticsearch, NotFoundError

from backend.storage.card import Card, CardDAO


class Indexer(object):

    def __init__(self, elasticsearch_client: Elasticsearch, card_dao: CardDAO, cards_index_alias: str):
        self.elasticsearch_client = elasticsearch_client
        self.card_dao = card_dao
        self.cards_index_alias = cards_index_alias

    def build_new_cards_index(self) -> str:
        index_name = "cards-" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.create_empty_cards_index(index_name)
        for card in self.card_dao.get_all():
            self.put_card_into_index(card, index_name)
        return index_name

    def create_empty_cards_index(self, index_name):
        self.elasticsearch_client.indices.create(index_name, {
            "mappings": {
                "properties": {
                    "name": {
                        "type": "text",
                        "analyzer": "english",
                    },
                    "text": {
                        "type": "text",
                        "analyzer": "english",
                    },
                    "tags": {
                        "type": "keyword",
                        "fields": {
                            "text": {
                                "type": "text",
                                "analyzer": "english",
                            },
                        },
                    },
                }
            }
        })

    def put_card_into_index(self, card: Card, index_name: str):
        self.elasticsearch_client.create(index_name, card.id, {
            "name": card.name,
            "text": card.markdown,
            "tags": card.tags,
        })

    def switch_current_cards_index(self, new_index_name: str):
        try:
            remove_actions = [
                {"remove": {"index": index_name, "alias": self.cards_index_alias}}
                for index_name in self.elasticsearch_client.indices.get_alias(name=self.cards_index_alias)
            ]
        except NotFoundError:
            # We don't have active index right now!
            # Not that uncommon when you start app from scratch via docker.
            remove_actions = []

        self.elasticsearch_client.indices.update_aliases({
            "actions": remove_actions + [{
                "add": {"index": new_index_name, "alias": self.cards_index_alias},
            }]
        })
