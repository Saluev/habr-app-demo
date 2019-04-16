import abc
from typing import Iterable

import bson
import bson.errors
from pymongo.collection import Collection


class MongoDAO(object, metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def collection(self) -> Collection:
        pass

    @property
    @abc.abstractmethod
    def object_class(self) -> type:
        pass

    @property
    @abc.abstractmethod
    def not_found_exception(self) -> type:
        pass

    def to_bson_middleware(self, document: dict) -> dict:
        if "id" in document:
            document["_id"] = bson.ObjectId(document.pop("id"))
        return document

    def to_bson(self, obj) -> dict:
        result = {
            k: v
            for k, v in obj.__dict__.items()
            if v is not None
        }
        result = self.to_bson_middleware(result)
        return result

    def from_bson_middleware(self, document: dict) -> dict:
        document["id"] = str(document.pop("_id"))
        return document

    def from_bson(self, document: dict):
        document = self.from_bson_middleware(document)
        return self.object_class(**document)

    def create(self, obj):
        obj.id = str(self.collection.insert_one(self.to_bson(obj)).inserted_id)
        return obj

    def update(self, obj):
        obj_id = bson.ObjectId(obj.id)
        self.collection.update_one({"_id": obj_id}, {"$set": self.to_bson(obj)})
        return obj

    def get_all(self) -> Iterable:
        for document in self.collection.find():
            yield self.from_bson(document)

    def get_by_id(self, obj_id: str):
        try:
            return self._get_by_query({"_id": bson.ObjectId(obj_id)})
        except bson.errors.InvalidId:
            raise ValueError

    def _get_by_query(self, query):
        document = self.collection.find_one(query)
        if document is None:
            raise self.not_found_exception()
        return self.from_bson(document)
