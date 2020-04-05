"""
Usage:

    docker-compose exec -T backend \
        python -m tools.generate_movie_events \
        < ~/Downloads/tmdb-movie-metadata/tmdb_5000_movies.csv \
        > ~/Downloads/habr-app-demo-dataset-events.csv

The dataset can be found at
    https://www.kaggle.com/tmdb/tmdb-movie-metadata
"""

import argparse
import csv
import json
import random
import sys

from backend.wiring import Wiring


parser = argparse.ArgumentParser()
parser.add_argument("--tags", type=int, default=50, help="number of tags to be sampled as queries")
parser.add_argument("--bigrams", type=int, default=950, help="number of bigrams to be sampled as queries")
parser.add_argument("--min-depth", type=int, default=10, help="minimum depth of single search session")
parser.add_argument("--max-depth", type=int, default=50, help="maximum depth of single search session")
parser.add_argument("--ctr", type=float, default=0.05, help="overall CTR")


if __name__ == "__main__":
    args = parser.parse_args()
    wiring = Wiring()

    reader = iter(csv.reader(sys.stdin))
    header = next(reader)

    title_index = header.index("title")
    keywords_index = header.index("keywords")
    overview_index = header.index("overview")

    all_tags = set()
    all_bigrams = set()

    for row in reader:
        title = row[title_index]
        keywords = [keyword["name"] for keyword in json.loads(row[keywords_index])]
        overview = row[overview_index]
        all_tags.update(keywords)
        words = overview.split()
        all_bigrams.update(map(" ".join, zip(words, words[1:])))

    tags = random.sample(all_tags, args.tags)
    bigrams = random.sample(all_bigrams, args.bigrams)
    queries = tags + bigrams

    cards = wiring.card_dao.get_all()
    card_by_id = {card.id: card for card in cards}

    writer = csv.writer(sys.stdout)
    writer.writerow(("query", "card_id", "event_type"))

    def generate_event(query: str, card_id: str, event_type: str):
        writer.writerow((query, card_id, event_type))

    for query in queries:
        depth = random.randint(args.min_depth, args.max_depth)
        search_result = wiring.searcher.search_cards(query, count=depth)
        found_card_ids = list(search_result.card_ids)
        actual_depth = len(found_card_ids)
        for position, card_id in enumerate(found_card_ids):
            generate_event(query, card_id, "view")
            # Let's artificially decrease probability of click for lower
            # ranked items to make TF-IDF feature most important.
            probability = 2 * args.ctr * (actual_depth - position - 1) / (actual_depth - 1) if actual_depth > 1 else args.ctr
            if random.random() < probability:
                generate_event(query, card_id, "click")
