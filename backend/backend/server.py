import os.path

import flask
import flask_cors

from backend.storage.card import CardNotFound
from backend.wiring import Wiring


env = os.environ.get("APP_ENV", "dev")
print(f"Starting application in {env} mode")


class HabrAppDemo(flask.Flask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        flask_cors.CORS(self, supports_credentials=True)

        self.wiring = Wiring(env)

        self.route("/api/v1/card/<card_id_or_slug>")(self.card)
        self.route("/api/v1/cards/search", methods=["POST"])(self.search_cards)

    def card(self, card_id_or_slug):
        try:
            card = self.wiring.card_dao.get_by_slug(card_id_or_slug)
        except CardNotFound:
            try:
                card = self.wiring.card_dao.get_by_id(card_id_or_slug)
            except (CardNotFound, ValueError):
                return flask.abort(404)
        return flask.jsonify({
            k: v
            for k, v in card.__dict__.items()
            if v is not None
        })

    def search_cards(self):
        request = flask.request.json
        search_result = self.wiring.searcher.search_cards(**request)
        cards = self.wiring.card_dao.get_by_ids(search_result.card_ids)
        return flask.jsonify({
            "totalCount": search_result.total_count,
            "cards": [
                {
                    "id": card.id,
                    "slug": card.slug,
                    "name": card.name,
                    # We don't need all card fields, or the payload will be too large.
                } for card in cards
            ],
            "nextCardOffset": search_result.next_card_offset,
            "tagStats": [
                {
                    "tag": stats.tag,
                    "cardCount": stats.cards_count,
                }
                for stats in search_result.tag_stats
            ]
        })


app = HabrAppDemo("habr-app-demo")
app.config.from_object(f"backend.{env}_settings")
app.secret_key = "nu privet habravchanin"
