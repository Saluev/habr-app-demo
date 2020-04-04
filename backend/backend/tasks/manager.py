from celery import Celery

from backend.tasks.index import index
from backend.tasks.parse import parse_card_markup


class TaskManager(object):
    def __init__(self, celery_app: Celery):
        self.celery_app = celery_app

    def enqueue_parsing_card_markup(self, card_id: str):
        self.celery_app.send_task(self._get_name(parse_card_markup), kwargs={"card_id": card_id})

    def enqueue_building_cards_index(self):
        self.celery_app.send_task(self._get_name(index))

    def _get_name(self, task):
        return self.celery_app.gen_task_name(task.__name__, task.__module__)
