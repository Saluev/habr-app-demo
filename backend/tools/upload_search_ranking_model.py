"""
Usage:

    docker-compose exec -T backend python -m tools.upload_search_ranking_model < ~/Downloads/habr-app-demo-model.json
"""

import json
import sys

from backend.wiring import Wiring

if __name__ == "__main__":
    wiring = Wiring()
    model_json = json.load(sys.stdin)
    wiring.search_ranking_manager.upload_xgboost_model(model_json)
