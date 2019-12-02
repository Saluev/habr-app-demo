from backend.storage.card import Card, CardNotFound
from backend.tasks.parse import parse_card_markup
from backend.wiring import Wiring

wiring = Wiring()


def create_or_update(card):
    try:
        card.id = wiring.card_dao.get_by_slug(card.slug).id
        card = wiring.card_dao.update(card)
    except CardNotFound:
        card = wiring.card_dao.create(card)
    wiring.task_queue.enqueue_call(
        parse_card_markup, kwargs={"card_id": card.id})


create_or_update(Card(
    slug="helloworld",
    name="Hello, world!",
    markdown="""
This is a hello-world page. It can't really compete with the [demo page](demo).
"""))

create_or_update(Card(
    slug="demo",
    name="Demo Card!",
    markdown="""
Hi there, habrovchanin. You've probably got here from the awkward ["Hello, world" card](helloworld).

Well, **good news**! Finally you are looking at a **really cool card**!
"""
))
