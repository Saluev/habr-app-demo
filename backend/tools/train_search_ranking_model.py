"""
Usage:

    python backend/tools/train_search_ranking_model.py \
        --events ~/Downloads/habr-app-demo-dataset-events.csv \
        --features ~/Downloads/habr-app-demo-dataset-features.csv \
        -o ~/Downloads/habr-app-demo-model.json
"""

import argparse
import csv
import collections
import random

from matplotlib import pyplot as plt
import numpy as np
from sklearn import metrics
import xgboost

parser = argparse.ArgumentParser()
parser.add_argument("--events", type=str, help="path to events file", required=True)
parser.add_argument("--features", type=str, help="path to features file", required=True)
parser.add_argument("-o", "--output", type=str, help="path to target model file", required=True)


def read_features(path):
    with open(path) as f:
        reader = iter(csv.reader(f))
        header = next(reader)

        query_index = header.index("query")
        card_id_index = header.index("card_id")
        feature_names = [
            column_name
            for column_name in header
            if column_name not in ("query", "card_id")
        ]

        features = {}
        for row in reader:
            query = row[query_index]
            card_id = row[card_id_index]
            features[query, card_id] = [
                float(cell)
                for idx, cell in enumerate(row)
                if idx not in (query_index, card_id_index)
            ]

    return feature_names, features


def read_events(path):
    with open(path) as f:
        reader = iter(csv.reader(f))
        header = next(reader)

        query_index = header.index("query")
        card_id_index = header.index("card_id")
        event_type_index = header.index("event_type")

        events = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
        for row in reader:
            query = row[query_index]
            card_id = row[card_id_index]
            event_type = row[event_type_index]
            events[query][card_id][event_type] += 1

    return events


def make_dmatrix(queries, events, feature_names, features):
    result_rows = []
    result_labels = []
    for query in queries:
        for card_id, counts_by_event_type in events[query].items():
            if (query, card_id) not in features:
                continue
            ctr = counts_by_event_type["click"] / counts_by_event_type["view"]
            result_rows.append(features[query, card_id])
            result_labels.append(ctr)
    return xgboost.DMatrix(np.array(result_rows), label=np.array(result_labels), feature_names=feature_names)


def build_roc(target_test, test_preds):
    fpr, tpr, threshold = metrics.roc_curve(target_test, test_preds)
    roc_auc = metrics.auc(fpr, tpr)
    plt.title("Receiver Operating Characteristic")
    plt.plot(fpr, tpr, "b", label="AUC = %0.3f" % roc_auc)
    plt.legend(loc="lower right")
    plt.plot([0, 1], [0, 1], "r--")
    plt.ylabel("True Positive Rate")
    plt.xlabel("False Positive Rate")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.gca().set_aspect("equal", adjustable="box")


if __name__ == "__main__":
    args = parser.parse_args()

    feature_names, features = read_features(args.features)
    events = read_events(args.events)

    all_queries = set(events.keys())
    train_queries = random.sample(all_queries, int(0.8 * len(all_queries)))
    test_queries = all_queries - set(train_queries)

    train_dmatrix = make_dmatrix(train_queries, events, feature_names, features)
    test_dmatrix = make_dmatrix(test_queries, events, feature_names, features)

    param = {
        "max_depth": 2,
        "eta": 0.3,
        "objective": "binary:logistic",
        "eval_metric": "auc",
    }
    num_round = 10
    booster = xgboost.train(param, train_dmatrix, num_round, evals=((train_dmatrix, "train"), (test_dmatrix, "test")))
    booster.dump_model(args.output, dump_format="json")

    xgboost.plot_importance(booster)

    plt.figure()
    build_roc(test_dmatrix.get_label(), booster.predict(test_dmatrix))

    plt.show()
