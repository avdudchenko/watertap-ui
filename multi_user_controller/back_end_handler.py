from flask import Flask, request, redirect, Response, render_template
from waitress import serve
import requests
import time
import logging

import json
from start_unique_ui import start_uq_worker
import os
import re

# You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True
# app = Flask(__name__)
app = Flask(__name__, static_folder="../electron/ui/build", static_url_path="/")


SITE_NAME = "http://127.0.0.1:"
WWW_SITE_NAME = "https://avdsystems.xyz:443/watertap_ui"

ACTIVE_SESSIONS = {}


@app.route("/_backend_handler/new_user_request", methods=["POST"])
def index():
    return render_template("index.html")


def get_active_session(user):
    global ACTIVE_SESSIONS
    if ACTIVE_SESSIONS.get(user) is None:
        ACTIVE_SESSIONS[user] = requests.Session()
    return ACTIVE_SESSIONS


@app.route(
    "/watertap_ui_backend/<string:user>/<path:path>",
    methods=["GET", "POST", "OPTIONS", "DELETE"],
)
def proxy(user, path):
    global SITE_NAME
    global PORT_REFERENCE
    # path = string
    print("original_path", path)

    path = get_port(user, path)
    if path != False:
        req_string = request.query_string.decode()
        print("sent_path", f"{SITE_NAME}/watertap_ui_backend/{user}/{path}", req_string)
        print(f"{SITE_NAME}{path}", req_string)  # , request.method)
        ACTIVE_SESSIONS = get_active_session(user)
        if req_string != "":
            path = f"{path}?{req_string}"
        if request.method == "GET":
            ts = time.time()
            resp = ACTIVE_SESSIONS[user].get(f"{SITE_NAME}{path}")
            print("get", time.time() - ts)
            ts = time.time()
            excluded_headers = []
            excluded_headers = [
                "content-encoding",
                # "content-length",
                "transfer-encoding",
                # "content-type",
                # "connection",
            ]

            cors_header = ("Access-Control-Allow-Origin", "*")

            headers = [
                (name, value)
                for (name, value) in resp.raw.headers.items()
                if name.lower() not in excluded_headers
            ]
            headers.append(cors_header)
            print(headers)
            # print(resp.content)
            response = Response(resp.content, resp.status_code, headers)
            print("response", time.time() - ts)
            return response
        elif request.method == "POST":
            # print(request.get_data())
            resp = ACTIVE_SESSIONS[user].post(
                f"{SITE_NAME}{path}", data=request.get_data()
            )  # json=request.get_json())
            excluded_headers = [
                # "content-encoding",
                "content-length",
                # "transfer-encoding",
                "connection",
            ]
            cors_header = ("Access-Control-Allow-Origin", "*")
            headers = [
                (name, value)
                for (name, value) in resp.raw.headers.items()
                if name.lower() not in excluded_headers
            ]
            # print(resp.content)
            headers.append(cors_header)
            # print(headers)
            response = Response(resp.content, resp.status_code, headers)
            return response
        elif request.method == "DELETE":
            resp = ACTIVE_SESSIONS[user].delete(f"{SITE_NAME}{path}").content
            response = Response(resp.content, resp.status_code, headers)
        return response


if __name__ == "__main__":
    global uq_pipe
    uq_pipe = start_uq_worker(WWW_SITE_NAME)

    # app.run(debug=True, port=500)

    serve(app, host="127.0.0.1", port=500)
