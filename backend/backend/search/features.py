import abc
from typing import Mapping, Set

Features = Mapping[str, float]


class CardFeaturesDAO(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_or_update(self, card_id: str, features: Features):
        pass

    @abc.abstractmethod
    def get_by_card_id(self, card_id: str) -> Features:
        pass


class CardFeaturesNotFound(Exception):
    pass


class CardFeaturesManager:

    ALL_FEATURE_NAMES = {"rating"}

    def __init__(self, card_features_dao: CardFeaturesDAO):
        self.card_features_dao = card_features_dao

    def create_or_update(self, card_id: str, features: Features):
        all_feature_names = self.get_all_feature_names_set()
        for feature_name in features:
            if feature_name not in all_feature_names:
                raise ValueError(f"unlisted feature: {feature_name}")
        return self.card_features_dao.create_or_update(card_id, features)

    def get_by_card_id(self, card_id: str) -> Features:
        try:
            return self.card_features_dao.get_by_card_id(card_id)
        except CardFeaturesNotFound:
            return {}

    def get_all_feature_names_set(self) -> Set[str]:
        return self.ALL_FEATURE_NAMES
