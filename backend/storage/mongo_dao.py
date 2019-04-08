import abc
from typing import Iterable

import bson
import bson.errors
from pymongo.collection import Collection


class MongoNotFound(Exception):
    pass


class MongoDAO(object, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def collection(self) -> Collection:
        pass

    @classmethod
    @abc.abstractmethod
    def object_class(cls) -> type:
        pass

    @classmethod
    def to_bson(cls, obj):
        result = {
            k: v
            for k, v in obj.__dict__.items()
            if v is not None
        }
        if "id" in result:
            result["_id"] = bson.ObjectId(result.pop("id"))
        return result

    @classmethod
    def from_bson(cls, document):
        document["id"] = str(document.pop("_id"))
        return cls.object_class()(**document)

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
            raise MongoNotFound()
        return self.from_bson(document)
