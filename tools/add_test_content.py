from backend.storage.card import Card, CardNotFound
from backend.tasks.parse import parse_card_markup
from backend.wiring import Wiring

wiring = Wiring()

try:
    card = wiring.card_dao.get_by_slug("helloworld")
except CardNotFound:
    card = wiring.card_dao.create(Card(
        slug="helloworld",
        name="Hello, world!",
        markdown="""
This is a hello-world page.
    """))

wiring.task_queue.enqueue_call(
    parse_card_markup, kwargs={"card_id": card.id})
