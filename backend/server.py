import os.path

import flask
import flask_cors


class HabrAppDemo(flask.Flask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        flask_cors.CORS(self)


app = HabrAppDemo("habr-app-demo")

env = os.environ.get("APP_ENV", "dev")
print(f"Starting application in {env} mode")
app.config.from_object(f"backend.{env}_settings")

app.secret_key = "nu privet habravchanin"
