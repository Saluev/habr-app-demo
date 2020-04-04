# Usage:
#   docker-compose exec -T backend python -m tools.add_movies < ~/Downloads/tmdb-movie-metadata/tmdb_5000_movies.csv
#
# The dataset can be found at
#   https://www.kaggle.com/tmdb/tmdb-movie-metadata

import csv
import json
import re
import sys

from backend.storage.card import Card, CardNotFound
from backend.tasks.parse import parse_card_markup
from backend.wiring import Wiring


def create_or_update(card):
    try:
        card.id = wiring.card_dao.get_by_slug(card.slug).id
        card = wiring.card_dao.update(card)
    except CardNotFound:
        card = wiring.card_dao.create(card)
    wiring.task_queue.enqueue_call(
        parse_card_markup, kwargs={"card_id": card.id})


def generate_slug(title):
    words = re.findall(r"[a-z]+", title.lower())
    return "_".join(words)


if __name__ == "__main__":
    wiring = Wiring()

    reader = iter(csv.reader(sys.stdin))
    header = next(reader)

    id_index = header.index("id")
    title_index = header.index("title")
    keywords_index = header.index("keywords")
    overview_index = header.index("overview")

    for row in reader:
        title = row[title_index]
        keywords = [keyword["name"] for keyword in json.loads(row[keywords_index])]
        overview = row[overview_index]
        slug = generate_slug(title)
        create_or_update(Card(
            slug=slug,
            name=title,
            markdown=overview,
            tags=keywords,
        ))