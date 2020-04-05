import bson
import bson.errors
from pymongo.collection import Collection
from pymongo.database import Database

from backend.search.features import CardFeaturesDAO, Features, CardFeaturesNotFound


class MongoCardFeaturesDAO(CardFeaturesDAO):

    def __init__(self, mongo_database: Database):
        self.mongo_database = mongo_database

    @property
    def collection(self) -> Collection:
        return self.mongo_database["card_features"]

    def create_or_update(self, card_id: str, features: Features):
        document_id = bson.ObjectId(card_id)
        self.collection.update_one({"_id": document_id}, {
            "$set": features
        }, upsert=True)

    def get_by_card_id(self, card_id: str) -> Features:
        try:
            return self._get_by_query({"_id": bson.ObjectId(card_id)})
        except bson.errors.InvalidId:
            raise ValueError

    def _get_by_query(self, query) -> Features:
        document = self.collection.find_one(query)
        if document is None:
            raise CardFeaturesNotFound()
        del document["_id"]
        return document
