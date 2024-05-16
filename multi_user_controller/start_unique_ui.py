import os
import subprocess
import time
import json
import multiprocessing
from multiprocessing import Pipe
import random

global NUMBER_OF_RUNNING_UIS
global BUFFER
NUMBER_OF_RUNNING_UIS = 3
BUFFER = 2


class uq_manager:
    def __init__(self, base_url="http://localhost:500/watertap_ui"):
        self.current_apps = {}
        self.current_lookup = {}
        self.current_rcs = {}
        self.front_port = 3000
        self.backend_port = 8000
        self.port_step = 2
        self.cur_unique_ui_id = 10000
        # self.cur_unique_ui_id += random.randrange(1000, 10000, 1)
        self.base_url = base_url
        self.used_apps = 0

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

            self.update_jsconfig(f"/watertap_ui/{ui_id}")
            rc = subprocess.Popen(
                "start_ui.bat", creationflags=subprocess.CREATE_NEW_CONSOLE
            )  # , shell=True)
            print("started")
            self.current_apps[ui_id] = {
                "frontend_port": str(front_port),
                "backend_port": str(backend_port),
                "user_name": "NA",
            }
            self.current_rcs[ui_id] = rc
            self.update_current_uqs()
            time.sleep(8)

    def generate_unique_UI(self, id_nums=5):
        print("Starting uniq ui", str(int(self.cur_unique_ui_id)))
        self.start_unique_ui(ui_id=str(int(self.cur_unique_ui_id)))
        self.cur_unique_ui_id += 10  # random.randrange(1000, 10000, 1)

    def assign_name_to_ui(self, name):
        if self.current_lookup.get(name) is None:
            for ui_id in self.current_apps:
                if self.current_apps[ui_id]["user_name"] == "NA":
                    self.current_apps[ui_id]["user_name"] = name
                    self.current_lookup[name] = ui_id
                    self.used_apps += 1
                    self.update_lookup()
                    self.update_current_uqs()
                    break
        else:
            print(f"User {name} already exists")

    def update_current_uqs(self):
        with open("current_servers.json", "w") as f:
            json.dump(self.current_apps, f)

    def update_lookup(self):
        with open("current_lookup.json", "w") as f:
            json.dump(self.current_lookup, f)

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


def _uq_worker(pipe_in, base_url):
    uq = uq_manager(base_url)
    global NUMBER_OF_RUNNING_UIS
    global BUFFER
    start_pause = 8
    last_update = time.time() - start_pause
    while True:
        if pipe_in.poll():
            name = pipe_in.recv()
            print(f"Starting {name} UI")
            uq.assign_name_to_ui(name)
        elif (
            len(uq.current_apps) < NUMBER_OF_RUNNING_UIS
            or (len(uq.current_apps) - uq.used_apps) < BUFFER
        ) and (time.time() - last_update) > start_pause:

            uq.generate_unique_UI()
            last_update = time.time()
        else:
            time.sleep(0.25)


def start_uq_worker(base_url):
    request_in, request_out = Pipe()
    p = multiprocessing.Process(target=_uq_worker, args=(request_out, base_url))
    p.start()
    return request_in


if __name__ == "__main__":
    uq_pipe = start_uq_worker()
    uq_pipe.send("alex")
    # uq = uq_manager()
    # uq.start_unique_ui(front_port=3000, backend_port=8000, ui_id="alex")
    # # uq.start_unique_ui(front_port=3010, backend_port=8010, ui_id="ben")
