from pymongo.collection import Collection
from pymongo.database import Database

from backend.storage.card import Card, CardDAO, CardNotFound
from backend.storage.mongo_dao import MongoDAO


class MongoCardDAO(MongoDAO, CardDAO):

    def __init__(self, mongo_database: Database):
        self.mongo_database = mongo_database
        self.collection.create_index("slug", unique=True)

    @property
    def collection(self) -> Collection:
        return self.mongo_database["cards"]

    object_class = Card

    not_found_exception = CardNotFound

    def get_by_slug(self, slug: str) -> Card:
        return self._get_by_query({"slug": slug})
