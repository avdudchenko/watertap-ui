import sys
import os
import glob
import watertap
import re

from pathlib import Path


conda_prefix = os.environ["CONDA_PREFIX"]


def update_entry_points(entry_point_file):
    print(f"conda_prefix is {conda_prefix}")

    """ specify water tap path with setup.py file that contains entry points"""

    entry_points = []
    start_getting_entryies = False
    with open(entry_point_file, "r") as f:
        lines = f.readlines()
        for l in lines:
            entry_points.append(l)
    print(entry_points)
    try:
        if sys.platform == "darwin":
            print("darwin")
            entrypoints_src_path = f"{conda_prefix}/lib/python*/site-packages/watertap-*info/entry_points.txt"
            entrypoints_dst_path = f"{conda_prefix}/lib/python*/site-packages/setuptools-*info/entry_points.txt"
        elif sys.platform == "linux":
            print("linux")
            entrypoints_src_path = f"{conda_prefix}/lib/python*/site-packages/watertap-*info/entry_points.txt"
            entrypoints_dst_path = f"{conda_prefix}/lib/python*/site-packages/setuptools-*info/entry_points.txt"
        else:
            # print("windows")
            entrypoints_src_path = (
                f"{conda_prefix}/lib/site-packages/watertap-*info/entry_points.txt"
            )
            entrypoints_dst_path = (
                f"{conda_prefix}/lib/site-packages/setuptools-*info/entry_points.txt"
            )
    except Exception as e:
        print(f"unable to get entry points src/dst: {e}")

    print(f"globbing from {entrypoints_src_path} to {entrypoints_dst_path}")

    entrypoints_src = glob.glob(entrypoints_src_path)[0]
    entrypoints_dst = glob.glob(entrypoints_dst_path)[0]
    # get entry points from src
    for entry_point in [entrypoints_src, entrypoints_dst]:
        cur_file = []
        with open(entry_point, "r", newline="") as f:
            non_watertap_entry = True
            k = 0
            for i in f:
                if "[watertap.flowsheets]" in i:
                    non_watertap_entry = False
                elif non_watertap_entry == False and len(i) == 1:
                    non_watertap_entry = True
                if non_watertap_entry:
                    cur_file.append(i)
                    # print(k, non_watertap_entry, i, len(i))
                k += 1
        with open(entry_point, "w", newline="") as f:
            for l in cur_file:
                f.write(f"{l}")
            f.write(f"[watertap.flowsheets]\n")
            for ep in entry_points:
                print("writing entery point", ep)
                f.write(f"{ep}\n")


if __name__ == "__main__":
    update_entry_points("kenya_entry_point_file.txt")
