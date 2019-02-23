from backend.storage.card import Card
from backend.wiring import Wiring

wiring = Wiring()

wiring.card_dao.create(Card(
    slug="helloworld",
    name="Hello, world!",
    markdown="""
This is a hello-world page.
"""))
