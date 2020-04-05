"""
Usage:

    docker-compose exec -T backend \
        python -m tools.compute_features \
        < ~/Downloads/habr-app-demo-dataset-events.csv \
        > ~/Downloads/habr-app-demo-dataset-features.csv
"""

import csv
import itertools
import sys

import tqdm

from backend.wiring import Wiring

if __name__ == "__main__":
    wiring = Wiring()

    reader = iter(csv.reader(sys.stdin))
    header = next(reader)

    feature_names = wiring.search_ranking_manager.get_feature_names()
    writer = csv.writer(sys.stdout)
    writer.writerow(["query", "card_id"] + feature_names)

    query_index = header.index("query")
    card_id_index = header.index("card_id")

    chunks = itertools.groupby(reader, lambda row: row[query_index])
    for query, rows in tqdm.tqdm(chunks):
        card_ids = [row[card_id_index] for row in rows]
        features = wiring.search_ranking_manager.compute_cards_features(query, card_ids)
        for card_id in card_ids:
            if card_id not in features:
                # Probably we couldn't find card by given query.
                continue
            writer.writerow((query, card_id, *features[card_id]))
