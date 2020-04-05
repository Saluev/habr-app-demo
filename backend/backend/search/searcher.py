import abc
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass
class TagStats:
    tag: str
    cards_count: int


@dataclass
class CardSearchResult:
    total_count: int
    card_ids: Iterable[str]
    next_card_offset: Optional[int]
    tag_stats: Iterable[TagStats]


class Searcher(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def search_cards(self, query: str = "", count: int = 20, offset: int = 0,
                     tags: Optional[Iterable[str]] = None, ids: Optional[Iterable[str]] = None) -> CardSearchResult:
        pass
