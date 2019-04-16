import json
import logging
import os.path
import sys

import flask
import flask_cors

from backend.storage.card import CardNotFound
from backend.wiring import Wiring


env = os.environ.get("APP_ENV", "dev")
logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', stream=sys.stderr, level=logging.DEBUG)
logging.info(f"Starting application in %s mode", env)


class HabrAppDemo(flask.Flask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        flask_cors.CORS(self)

        self.wiring = Wiring(env)

        self.route("/api/v1/card/<card_id_or_slug>")(self.card)

        self.route("/api/v1/session/create")(self.create_session)
        self.route("/api/v1/session/<session_id>/events")(self.events)
        self.route("/api/v1/session/<session_id>/join")(self.join_room)
        self.route("/api/v1/session/<session_id>/action", methods=("POST",))(self.action)

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

    def create_session(self):
        session = self.wiring.session_manager.create_session()
        client_session = self.wiring.session_client_converter.to_json(session)
        return flask.jsonify(client_session)

    def events(self, session_id):
        def generator():
            yield ""  # Add some magic (clearly experience-based).
            for data in self.wiring.session_manager.yield_events(session_id):
                yield f"data:{json.dumps(data)}\n\n".encode("ascii")
        resp = flask.Response(generator(), mimetype="text/event-stream")
        resp.headers["Cache-Control"] = "no-cache"
        return resp

    def action(self, session_id):
        action = flask.request.get_json()
        self.wiring.actions_manager.push_action(session_id, action)
        return flask.jsonify({"status": "ok"})

    def join_room(self, session_id):
        room_id, is_full = self.wiring.room_manager.choose_room_for_participant(session_id)
        if is_full:
            room = self.wiring.room_dao.get_by_id(room_id)
            self.wiring.game_server_client.schedule_game(room)
        room = self.wiring.room_dao.get_by_id(room_id)
        client_room = self.wiring.room_client_converter.to_json(room)
        return flask.jsonify(client_room)


app = HabrAppDemo("habr-app-demo")
app.config.from_object(f"backend.{env}_settings")
app.secret_key = "nu privet habravchanin"
