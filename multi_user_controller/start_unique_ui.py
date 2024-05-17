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
NUMBER_OF_RUNNING_UIS = 15
BUFFER = 5


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
        self._cont=0

    def start_unique_ui(
        self,
        front_port=None,
        backend_port=None,
        ui_id="123",
    ):
        print(ui_id,self.current_rcs.keys(), self._cont)
        if str(ui_id) not in self.current_rcs:
            if front_port is None:
                front_port = self.front_port + self.port_step
                self.front_port = front_port
            if backend_port is None:
                backend_port = self.backend_port + self.port_step
                self.backend_port = backend_port
            # configure .env for UI
            with open("../electron/ui/.env", "w") as writer:
                writer.write(f"REACT_APP_BACKEND_SERVER={self.base_url}/{str(ui_id)}\n")
                writer.write(
                    f"REACT_APP_FRONTEND_SERVER={self.base_url}/{str(ui_id)}\n"
                )
                writer.write(f"REACT_APP_BACKEND_PORT={backend_port}\n")
                writer.write(f"REACT_APP_FRONTEND_PORT={front_port}\n")
                writer.write(f"port={front_port}\n")
                writer.write(f"BROWSER=none\n")
                writer.write(f"user_id={str(ui_id)}")

            print(f"start {ui_id}")
            self.update_jsconfig(f"/watertap_ui/{str(ui_id)}")
            backend_location = self.watertap_ui_path / "backend" / "app" / "main.py"
            self.current_rcs[str(ui_id)] = 'temp'
            
            print("started")
            self.current_apps[str(ui_id)] = {
                "frontend_port": str(front_port),
                "backend_port": str(backend_port),
                "user_name": "NA",
            }
            rc = subprocess.Popen(
                "start_ui.bat",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            self.current_rcs[str(ui_id)] = rc
            self.update_current_uqs()
            # time.sleep(8)
            print('Started new ui test on ', f"http://127.0.0.1:{backend_port}/")
            return f"http://127.0.0.1:{backend_port}/"
        else:
            return f"http://127.0.0.1:{self.current_apps[str(ui_id)]['backend_port']}/"

    def generate_unique_UI(self, id_nums=None):
        
        if id_nums is None:
            print('auto start up')
            while (str(self.cur_unique_ui_id) in str(self.current_apps.keys()) 
            or str(self.cur_unique_ui_id) in str([self.user_lookup[user]['user_id'] for user in self.user_lookup])):
                self.cur_unique_ui_id += 10
            print("Starting uniq ui", str(int(self.cur_unique_ui_id)))
            result = self.start_unique_ui(ui_id=str(int(self.cur_unique_ui_id)))
        else:
            print("Starting provided ui", str(int(id_nums)))
            result = self.start_unique_ui(ui_id=str(id_nums))
        return result

    def assign_name_to_ui(self, name):
        assigned=False
        last_request=None
        if self.user_lookup.get(name) is None:
            for ui_id in self.current_apps:
                if self.current_apps[str(ui_id)]["user_name"] == "NA":
                    self.current_apps[str(ui_id)]["user_name"] = name
                    self.user_lookup[name] = {
                        "user_id": str(ui_id),
                        "first_login": True,
                    }
                    self.live_servers[name] = [str(ui_id)]
                    self.used_apps += 1
                    self.update_lookup()
                    self.update_current_uqs()
                    return True, last_request

        else:
            print(f"User {name} already exists")
            if self.current_apps.get(self.user_lookup[name]["user_id"]) == None:
                print(f'FORCING STARTUP!')
                last_request=self.generate_unique_UI(id_nums=self.user_lookup[name]["user_id"])
                self.used_apps += 1
            else:
                self.current_apps[self.user_lookup[name]["user_id"]]['user_name']=name
            self.user_lookup[name]["first_login"] = False

            self.update_lookup()
            return True, last_request
        return assigned, last_request

    def update_current_uqs(self):
        with open("current_servers.json", "w") as f:
            json.dump(self.current_apps, f)

    def update_lookup(self):
        with open("user_lookup.json", "w") as f:
            json.dump(self.user_lookup, f)

    def load_prior_setting(self):
        try:
            with open("user_lookup.json") as f:
                self.user_lookup = json.load(f)
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
    name_que=[]
    cur_time=time.time()
    u_time=time.time()
    update_time=60
    while True:
        if pipe_in.poll():
            name = pipe_in.recv()
            name_que.append(name)
            print(f"Starting {name} UI")
        if last_request is None or request_check(last_request): 
            for name in name_que[:]:
                result, _last_request = uq.assign_name_to_ui(name)
                if result:
                    name_que.remove(name)
                    print(f'removed {name}, {name_que}')
                if _last_request is not None:
                    last_request=_last_request
                    break
        if len(name_que)==0:
            if (
                len(uq.current_apps) < NUMBER_OF_RUNNING_UIS
                or (len(uq.current_apps) - uq.used_apps) < BUFFER
            ):  
                print('starting_uq', last_request,"running_uis", len(uq.current_apps) , NUMBER_OF_RUNNING_UIS, 
                "buffer",(len(uq.current_apps) - uq.used_apps) , BUFFER, cur_time)
                if last_request is None:
                    last_request = uq.generate_unique_UI()
                elif request_check(last_request):
                    last_request = uq.generate_unique_UI()
                
            if time.time()-u_time>update_time:
                print(last_request,"running_uis", len(uq.current_apps) , NUMBER_OF_RUNNING_UIS, 
                "buffer",(len(uq.current_apps) - uq.used_apps) , BUFFER, cur_time)
                u_time=time.time()
        time.sleep(0.2)


def start_uq_worker(base_url):
    request_in, request_out = Pipe()
    p = multiprocessing.Process(target=_uq_worker, args=(request_out, base_url))
    p.start()
    return request_in


if __name__ == "__main__":
    uq_pipe = start_uq_worker(base_url="test")
    # uq_pipe.send("alex")
    # uq = uq_manager()
    # uq.start_unique_ui(front_port=3000, backend_port=8000, str(ui_id)="alex")
    # # uq.start_unique_ui(front_port=3010, backend_port=8010, str(ui_id)="ben")
