from flask import Flask, request, redirect, Response, render_template
from waitress import serve
import requests
import time
import logging

import json
from start_unique_ui import start_uq_worker
import os
import re
import hashlib

# You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True
# app = Flask(__name__)
app = Flask(__name__, static_folder="../electron/ui/build", static_url_path="/")


SITE_NAME = "http://127.0.0.1:"
WWW_SITE_NAME = "https://teremesystems.com:443/watertap_ui"
BACKEND_SERVER = "http://127.0.0.1:501"
ACTIVE_SESSIONS = {}
BACKEND_SESSION = requests.session()
SERVER_LOCATION = "teremesystems.com"


def load_current_port_refs():
    for i in range(10):
        try:
            f = open("server_configs/current_servers.json")
            return json.load(f)
        except IOError:
            time.sleep(0.5)
            pass
    return {}


def load_current_lookup_table():
    for i in range(10):
        try:
            f = open("server_configs/user_lookup.json")
            return json.load(f)
        except IOError:
            time.sleep(0.5)
            pass
    return {}


def load_accepted_users():
    for i in range(10):
        try:
            f = open("server_configs/accepted_users.json")
            return json.load(f)
        except IOError:
            time.sleep(0.5)
            pass
    return {}


def inplace_change(location, filename, old_string, new_string, modname=None):
    with open(os.path.join(location, filename)) as f:
        s = f.read()
    if modname is not None:
        sf = filename.split(".")[-1]
        filename.replace("." + sf, "")
        filename = filename + str(modname) + "." + sf
    with open(os.path.join(location, filename), "w") as f:
        print('Changing "{old_string}" to "{new_string}" in {filename}')

        s = re.sub(old_string, new_string, s)
        f.write(s)
    return filename


@app.route("/watertap_ui/<string:user>")
def ui_index(user):
    path = inplace_change(
        "../electron/ui/build",
        "index.html",
        "watertap_ui/?(.*?)/",
        f"watertap_ui/{user}/",
        modname=user,
    )
    return app.send_static_file(path)


@app.route("/watertap_ui/<string:user>/<path:path>")
def ui(user, path):
    print(user, path)
    if ".js" in path and ".js.map" not in path:
        if user is not None:
            path = inplace_change(
                "../electron/ui/build",
                path,
                "https://avdsystems.xyz:443/watertap_ui/?(.*?)/",
                f"https://avdsystems.xyz:443/watertap_ui_backend/{user}/",
                modname=user,
            )
        else:
            raise ValueError
    print(path)
    result = app.send_static_file(path)
    return result


def get_port(user, path):
    PORT_REFERENCE = load_current_port_refs()
    if user in PORT_REFERENCE.keys():
        if "flowsheets" in path:
            path = f'{PORT_REFERENCE[user]["backend_port"]}/{path}'
            print("updated path", path)
            return path
        else:
            path = f'{PORT_REFERENCE[user]["frontend_port"]}/{path}'
            print("updated path", path)
            return path
    else:
        return False


def send_user_name(name, userid, backend):
    global BACKEND_SESSION
    global BACKEND_SERVER
    url = f"{BACKEND_SERVER}/new_user_request"
    payload = {"username": name, "id": userid, "backend": backend}
    BACKEND_SESSION.post(url, json=payload)


def encode(string_value):
    h = hashlib.new("sha256")
    h.update(string_value.encode())
    return str(h.hexdigest())


@app.route("/start_new_ui_instance", methods=["GET", "POST"])
def start_new_ui_instance():
    print(request)
    username = request.form["username"]
    pwd = request.form["pwd"]
    print("Got username and pwd", username, pwd)
    username_id = encode(f"{username}:{pwd}")
    backend = encode(f"{pwd}")
    print("Got backend request", backend)
    lookup = load_accepted_users()
    print("Got lookup table", lookup)
    if backend in lookup.keys():
        global ACTIVE_SESSIONS
        global BACKEND_SESSION
        # try:
        working_name = f"{username}_{lookup[backend]['backend_name']}"
        send_user_name(working_name, username_id, backend)
        got_user = False
        for i in range(60):
            time.sleep(1)
            lookup = load_current_lookup_table()
            print(lookup)
            print(working_name)
            user_id_data = lookup.get(working_name)
            if user_id_data is not None:
                user_id = user_id_data["user_id"]
                first_login = user_id_data["first_login"]
                print(user_id_data)
                if first_login == True:
                    unique_user_message = f"This is your first login, use username: {username}, to re-access saved flowsheet configurations!"
                else:
                    unique_user_message = f"Thank you for returning {username}, if this is your FIRST time accessing UI please return and enter a NEW user name!"
                global ACTIVE_SESSIONS
                ACTIVE_SESSIONS[user_id] = requests.Session()

                return render_template(
                    "ui_redirect.html",
                    url_refresh=f"5;URL={WWW_SITE_NAME}/{user_id}",
                    unique_user_message=unique_user_message,
                    user_link=f"{WWW_SITE_NAME}/{user_id}",
                )  # redirect(f"/watertap_ui/{username}")
        # except requests.exceptions.ConnectionError:
        #  pass

        return render_template(
            "user_creation_failed.html",
            url_refresh=f"5;URL=https://{SERVER_LOCATION}:443",
            user_link=f"https://{SERVER_LOCATION}:443",
        )
    else:
        return render_template(
            "failed_login.html",
            url_refresh=f"2;URL=https://{SERVER_LOCATION}:443",
            user_link=f"https://{SERVER_LOCATION}:443",
        )


@app.route("/")
def index():
    return render_template("login_page.html")


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
            resp = ACTIVE_SESSIONS[user].get(f"{SITE_NAME}{path}", timeout=None)
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

    serve(app, host="127.0.0.1", port=500, threads=7)
