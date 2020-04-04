import rq

from backend.tasks.index import index
from backend.tasks.parse import parse_card_markup


class TaskManager(object):
    def __init__(self, task_queue: rq.Queue):
        self.task_queue = task_queue

    def enqueue_parsing_card_markup(self, card_id: str):
        self.task_queue.enqueue_call(
            parse_card_markup, kwargs={"card_id": card_id})

    def enqueue_building_cards_index(self):
        self.task_queue.enqueue_call(index)
