from flask import Flask, request, jsonify, redirect, Response, render_template
from waitress import serve
import requests
import time
import logging

import json
from start_unique_ui import start_uq_worker, uq_manager
import os
import re

from dotenv import load_dotenv

load_dotenv()

# You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True
# app = Flask(__name__)


WATERT_UI_LINK = os.getenv("WATERT_UI_LINK", "http://127.0.0.1:2000/watertap_ui")
UNIQUE_SESSION_HANDLER = os.getenv(
    "UNIQUE_SESSION_HANDLER", "http://localhost:2001"
)
WATERTAP_UI_PATH = os.getenv("WATERTAP_UI_PATH", "../electron/build")

app = Flask(
    __name__,
    static_folder=WATERTAP_UI_PATH,
    static_url_path="/",
)

ACTIVE_SESSIONS = {}


@app.route("/new_user_request", methods=["POST"])
def start_new_user():
    global uq_pipe
    new_user = request.get_json()
    print("new_user_request got", new_user)
    uq_pipe.put(new_user)
    return f"{new_user} added!"


@app.route("/get_current_users", methods=["GET"])
def get_servers():
    global uqm
    uqm.load_servers()

    return jsonify(uqm.current_apps)


if __name__ == "__main__":
    global uq_pipe
    global uqm
    uqm = uq_manager(UNIQUE_SESSION_HANDLER)
    uq_pipe = start_uq_worker(WATERT_UI_LINK)
    # app.run(debug=True, port=500)
    serve(app, host="127.0.0.1", port=2001)
