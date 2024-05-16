from flask import Flask, request, redirect, Response, render_template

import requests
import time
import logging

import json
from start_unique_ui import start_uq_worker

# You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True
app = Flask(__name__, static_folder="../electron/ui/build", static_url_path="/")

SITE_NAME = "http://127.0.0.1:"
WWW_SITE_NAME = "https://avdsystems.xyz:443/watertap_ui"


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/watertap_ui/10030/static/js/main.e81501ae.js")
def ui():
    return app.send_static_file("static/js/main.e81501ae.js")


if __name__ == "__main__":
    # global uq_pipe
    # uq_pipe = start_uq_worker(WWW_SITE_NAME)

    app.run(debug=True, port=500)
