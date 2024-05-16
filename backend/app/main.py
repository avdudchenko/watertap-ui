import sys
import os
import logging
import uvicorn
import multiprocessing
import idaes.logger as idaeslog

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from fastapi import FastAPI
from app.internal.get_extensions import check_for_idaes_extensions, get_idaes_extensions
from app.routers import flowsheets
from fastapi.middleware.cors import CORSMiddleware
import watertap_ui

from pathlib import Path


_log = idaeslog.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flowsheets.router)


@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}


def get_env():

    env_loc = Path(__file__).parents[2]
    loc = env_loc / "electron" / "ui" / ".env"
    with open(loc) as reader:
        for line in reader.readlines():
            print(line)
            if "REACT_APP_BACKEND_PORT" in str(line):
                line = str(line).split("=")
                port = int(line[-1])
                break
    return port


if __name__ == "__main__":
    port = get_env()
    if "i" in sys.argv or "install" in sys.argv:
        _log.info("running get_extensions()")
        if not check_for_idaes_extensions():
            get_idaes_extensions()

    elif "d" in sys.argv or "dev" in sys.argv:
        _log.info(f"starting app")
        multiprocessing.freeze_support()
        uvicorn.run("__main__:app", host="127.0.0.1", port=port, reload=True)

    else:
        print(f"backend port is, {port}, runing in non dev mode")
        _log.info(f"starting app")
        multiprocessing.freeze_support()
        uvicorn.run(app, host="127.0.0.1", port=port, reload=False)
