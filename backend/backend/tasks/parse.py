import mistune

from backend.storage.card import CardDAO
from backend.tasks.task import task


@task
def parse_card_markup(card_dao: CardDAO, card_id: str):
    card = card_dao.get_by_id(card_id)
    card.html = _parse_markdown(card.markdown)
    card_dao.update(card)


_parse_markdown = mistune.create_markdown(escape=True, hard_wrap=False)
