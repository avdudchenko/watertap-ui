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


def load_current_port_refs():
    for i in range(10):
        try:
            f = open("current_servers.json")
            return json.load(f)
        except IOError:
            pass


def load_current_lookup_table():
    for i in range(10):
        try:
            f = open("user_lookup.json")
            return json.load(f)
        except IOError:
            pass


def inplace_change(location, filename, old_string, new_string, modname=None):
    # Safely read the input filename using 'with'
    with open(os.path.join(location, filename)) as f:
        s = f.read()
        # if old_string not in s:
        #     print('"{old_string}" not found in {filename}.'.format(**locals()))
        #     return filename
    if modname is not None:
        sf = filename.split(".")[-1]
        filename.replace("." + sf, "")
        filename = filename + str(modname) + "." + sf
    # Safely write the changed content, if found in the file
    with open(os.path.join(location, filename), "w") as f:
        print(
            'Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals())
        )
        s = re.sub(old_string, new_string, s)
        f.write(s)
    return filename


@app.route("/watertap_ui/<int:user>")
def ui_index(user):
    path = inplace_change(
        "../electron/ui/build",
        "index.html",
        "watertap_ui/?(.*?)/",
        f"watertap_ui/{user}/",
        modname=user,
    )
    return app.send_static_file(path)


@app.route("/watertap_ui/<int:user>/<path:path>")
def ui(user, path):
    print(user, path)
    if ".js" in path:
        path = inplace_change(
            "../electron/ui/build",
            path,
            "https://avdsystems.xyz:443/watertap_ui/?(.*?)/",
            f"https://avdsystems.xyz:443/watertap_ui_backend/{user}/",
            modname=user,
        )
    print(path)
    result = app.send_static_file(path)
    return result


def get_port(path):
    PORT_REFERENCE = load_current_port_refs()
    path_split = path.split("/")
    if "flowsheets" in path:

        path = path.replace(
            path_split[0],
            PORT_REFERENCE[f"{path_split[0]}"]["backend_port"],  # /flowsheets"]
        )
        print("updated path", path)
        return path
    elif path_split[0] in PORT_REFERENCE.keys():
        path = path.replace(
            path_split[0], PORT_REFERENCE[f"{path_split[0]}"]["frontend_port"]
        )
        print("updated path", path)
        return path
    else:
        return False


# @app.route("/watertap_ui/<string:user>/static/js/bundle.js", methods=["GET", "POST"])
# def manual_load(user):
#     PORT_REFERENCE = load_current_port_refs()
#     resp = requests.get(
#         f"{SITE_NAME}{PORT_REFERENCE[user]['frontend_port']}/watertap_ui/{user}/static/js/bundle.js"
#     )
#     cors_header = ("Access-Control-Allow-Origin", "*")
#     excluded_headers = [
#         "content-encoding",
#         # "content-length",
#         "transfer-encoding",
#         # "content-type",
#         # "connection",
#     ]
#     headers = [
#         (name, value)
#         for (name, value) in resp.raw.headers.items()
#         if name.lower() not in excluded_headers
#     ]
#     headers.append(cors_header)
#     response = Response(resp.content, resp.status_code, headers)
#     return response


@app.route("/start_new_ui_instance", methods=["GET", "POST"])
def start_new_ui_instance():
    print(request)
    username = request.form["username"]
    global uq_pipe
    uq_pipe.send(username)
    for i in range(60):
        time.sleep(2)
        lookup = load_current_lookup_table()

        user_id_data = lookup.get(username)
        if user_id_data is not None:
            user_id = user_id_data["user_id"]
            first_loging = user_id_data["first_login"]
            print(user_id_data)
            if first_loging == True:
                unique_user_message = f"This is your first login, use username: {username}, to re-access saved flowsheet configurations!"
            else:
                unique_user_message = f"Thank you for returning {username}, if this is your FIRST time accessing UI please return and enter a NEW user name!"
            
            break

    return render_template(
        "ui_redirect.html",
        url_refresh=f"5;URL={WWW_SITE_NAME}/{user_id}",
        unique_user_message=unique_user_message,
        user_link=f"{WWW_SITE_NAME}/{user_id}",
    )  # redirect(f"/watertap_ui/{username}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route(
    "/watertap_ui_backend/<path:path>", methods=["GET", "POST", "OPTIONS", "DELETE"]
)
def proxy(path):
    global SITE_NAME
    global PORT_REFERENCE
    # path = string
    print("original_path", path)

    path = get_port(path)
    if path != False:
        req_string = request.query_string.decode()
        print("sent_path", f"{SITE_NAME}/watertap_ui_backend/{path}", req_string)
        print(f"{SITE_NAME}{path}", req_string)  # , request.method)
        if req_string != "":
            path = f"{path}?{req_string}"
        if request.method == "GET":
            ts = time.time()
            resp = requests.get(f"{SITE_NAME}{path}")
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
            # if "list" in path:
            #     print(path)
            #     print(resp.raw.headers)
            #     print("responce", resp.json())

            #     resp_data = resp.json()
            # else:
            #     resp_data = resp.content
            #     # respo.content.js
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
            resp = requests.post(
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
            resp = requests.delete(f"{SITE_NAME}{path}").content
            response = Response(resp.content, resp.status_code, headers)
        return response


if __name__ == "__main__":
    global uq_pipe
    uq_pipe = start_uq_worker(WWW_SITE_NAME)

    # app.run(debug=False, port=500)
    serve(app, host="http://localhost", port=500)
