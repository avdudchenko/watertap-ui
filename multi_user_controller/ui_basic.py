from flask import Flask, request, redirect, Response, render_template

import requests
import time
import logging

import json
from start_unique_ui import start_uq_worker
import re
import os

# You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True
app = Flask(__name__, static_folder="../electron/ui/build", static_url_path="/")

SITE_NAME = "http://127.0.0.1:"
WWW_SITE_NAME = "https://temeresystems.com:443/watertap_ui"


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
def index(user):
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
            "static/js/main.4ce4f469.js",
            "https://avdsystems.xyz:443/watertap_ui/?(.*?)/",
            f"https://avdsystems.xyz:443/watertap_ui/{user}/",
            modname=user,
        )
    print(path)
    result = app.send_static_file(path)
    return result


if __name__ == "__main__":
    # global uq_pipe
    # uq_pipe = start_uq_worker(WWW_SITE_NAME)

    app.run(debug=True, port=2000)
