import os
import subprocess
import time
import json
import multiprocessing
from multiprocessing import Pipe
import random
import watertap_ui

from pathlib import Path
import requests

global NUMBER_OF_RUNNING_UIS
global BUFFER
NUMBER_OF_RUNNING_UIS = 25
BUFFER = 2


class uq_manager:
    def __init__(self, base_url="http://localhost:500/watertap_ui"):
        self.current_apps = {}
        self.user_lookup = {}
        self.live_servers = {}
        self.current_rcs = {}
        self.load_prior_setting()
        self.front_port = 3000
        self.backend_port = 8000
        self.port_step = 2
        self.cur_unique_ui_id = 10000
        self.base_url = base_url
        self.used_apps = 0
        self.watertap_ui_path = Path(__file__).parent.parent

    def start_unique_ui(
        self,
        front_port=None,
        backend_port=None,
        ui_id="123",
    ):
        if ui_id not in self.current_rcs:
            if front_port is None:
                front_port = self.front_port + self.port_step
                self.front_port = front_port
            if backend_port is None:
                backend_port = self.backend_port + self.port_step
                self.backend_port = backend_port
            # configure .env for UI
            with open("../electron/ui/.env", "w") as writer:
                writer.write(f"REACT_APP_BACKEND_SERVER={self.base_url}/{ui_id}\n")
                writer.write(f"REACT_APP_FRONTEND_SERVER={self.base_url}/{ui_id}\n")
                writer.write(f"REACT_APP_BACKEND_PORT={backend_port}\n")
                writer.write(f"REACT_APP_FRONTEND_PORT={front_port}\n")
                writer.write(f"port={front_port}\n")
                writer.write(f"BROWSER=none\n")
                writer.write(f"user_id={ui_id}")

            print("started")
            self.update_jsconfig(f"/watertap_ui/{ui_id}")
            backend_location = self.watertap_ui_path / "backend" / "app" / "main.py"
            # rc = subprocess.run(
            #     [
            #         f"conda activate watertap-ui-env",
            #         f"python {backend_location} {backend_port}",
            #     ],
            #     stdout=subprocess.DEVNULL,
            #     stderr=subprocess.STDOUT,
            # )
            # time.sleep(1)
            # rc = subprocess.Popen(
            #     "start_ui.bat",
            #     # stdout=subprocess.DEVNULL,
            #     # stderr=subprocess.STDOUT,
            # )
            rc = subprocess.Popen(
                "start_ui.bat",
                # stdout=subprocess.DEVNULL,
                # stderr=subprocess.STDOUT,
            )
            print("started")
            self.current_apps[ui_id] = {
                "frontend_port": str(front_port),
                "backend_port": str(backend_port),
                "user_name": "NA",
            }
            self.current_rcs[ui_id] = rc
            self.update_current_uqs()
            # time.sleep(8)
            return f"http://127.0.0.1:{backend_port}/"
        return None

    def generate_unique_UI(self, id_nums=None):
        print("Starting uniq ui", str(int(self.cur_unique_ui_id)))
        if id_nums is None:
            while self.cur_unique_ui_id not in self.current_apps:
                self.cur_unique_ui_id += 10
            result = self.start_unique_ui(ui_id=str(int(self.cur_unique_ui_id)))
        else:
            result = self.start_unique_ui(ui_id=str(id_nums))
        return result

    def assign_name_to_ui(self, name):
        if self.user_lookup.get(name) is None:
            for ui_id in self.current_apps:
                if self.current_apps[ui_id]["user_name"] == "NA":
                    self.current_apps[ui_id]["user_name"] = name
                    self.user_lookup[name] = {"user_id": ui_id, "first_login": True}
                    self.live_servers[name] = [ui_id]
                    self.used_apps += 1
                    self.update_lookup()
                    self.update_current_uqs()
                    break
        else:
            print(f"User {name} already exists")
            if self.live_servers.get(name) == None:
                self.generate_unique_UI(id_nums=self.user_lookup[name]["user_id"])
            self.user_lookup[name]["first_login"] = False
            self.update_lookup()

    def update_current_uqs(self):
        with open("current_servers.json", "w") as f:
            json.dump(self.current_apps, f)

    def update_lookup(self):
        with open("user_lookup.json", "w") as f:
            json.dump(self.user_lookup, f)

    def load_prior_setting(self):
        try:
            with open("user_lookup.json") as f:
                self.current_apps = json.load(f)
        except FileNotFoundError:
            pass

    def update_jsconfig(self, address_base):
        for i in range(10):
            try:
                f = open(r"..\electron\ui\package.json")
                jsconfig = json.load(f)
                print(jsconfig)
                jsconfig["homepage"] = address_base
                break
            except IOError:
                pass
        with open(r"..\electron\ui\package.json", "w") as f:
            json.dump(jsconfig, f)


def request_check(url):
    try:
        r = requests.get(url, timeout=1)
        # print(r.content)
        r = r.json()
        return r["message"] == "Hello FastAPI"
    except requests.exceptions.ConnectTimeout:
        return False


def _uq_worker(pipe_in, base_url):
    uq = uq_manager(base_url)
    global NUMBER_OF_RUNNING_UIS
    global BUFFER
    last_request = None
    while True:
        if pipe_in.poll():
            name = pipe_in.recv()
            print(f"Starting {name} UI")
            uq.assign_name_to_ui(name)
        elif (
            len(uq.current_apps) < NUMBER_OF_RUNNING_UIS
            or (len(uq.current_apps) - uq.used_apps) < BUFFER
        ):
            if last_request is None:
                last_request = uq.generate_unique_UI()
            elif request_check(last_request):
                last_request = uq.generate_unique_UI()
        else:
            time.sleep(0.25)


def start_uq_worker(base_url):
    request_in, request_out = Pipe()
    p = multiprocessing.Process(target=_uq_worker, args=(request_out, base_url))
    p.start()
    return request_in


if __name__ == "__main__":
    uq_pipe = start_uq_worker(base_url="test")
    # uq_pipe.send("alex")
    # uq = uq_manager()
    # uq.start_unique_ui(front_port=3000, backend_port=8000, ui_id="alex")
    # # uq.start_unique_ui(front_port=3010, backend_port=8010, ui_id="ben")
