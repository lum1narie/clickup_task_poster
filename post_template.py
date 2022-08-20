import json
import os
import time
from datetime import datetime
from os.path import dirname, join
import requests

from clickup_api import *

from dotenv import load_dotenv

ENV_AUTH = "CLICKUP_AUTH"
ENV_LIST = "CLICKUP_LIST"
ENV_TEMPLATE = "CLICKUP_TEMPLATE"

# list file of tasks
TASK_FILE = "tasks"

# maximum API run in a minute
POST_PER_MIN = 60

if __name__ == "__main__":
    INTERVAL_MICROS = 1000000.0 * 60.0 / POST_PER_MIN

    # load dotenv
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    auth = os.environ.get(ENV_AUTH)
    list_id = os.environ.get(ENV_LIST)
    template_id = os.environ.get(ENV_TEMPLATE)

    # read task file
    task_path = join(dirname(__file__), TASK_FILE)
    with open(task_path, "r", encoding="utf-8") as f:
        task_lines_dup = [l for l in f.read().splitlines()]

    # remove duplicate task
    task_lines = []
    for line in task_lines_dup:
        if line == "" or line not in task_lines:
            task_lines.append(line)

    # ready client
    c = ClickUpClient(auth)

    remain_lines = []  # record failed task
    # post tasks
    for line in task_lines:
        # ignore blank line
        if line == "":
            remain_lines.append(line)
            continue

        # POST
        task = line
        print(f'Posting task "{task}"')

        # try POST
        r = c.create_task_template({"name":task}, list_id, template_id)
        if r is None:
            # when timeout
            print(f"time out ({c.TIMEOUT_SEC} sec.)")
        else:
            print(f"{r.status_code}: {r.reason}")
        print("-" * 60)


        if not (r is not None and r.status_code == 200):
            # record if fail
            remain_lines.append(task)

    # remove truncating ""
    while len(remain_lines) > 0 and remain_lines[-1] == "":
        remain_lines = remain_lines[:-1]
    # remove beggining ""
    while len(remain_lines) > 0 and remain_lines[0] == "":
        remain_lines = remain_lines[1:]
    # convert continuous "" into single ""
    for i in range(len(remain_lines) - 1, 0, -1):
        if remain_lines[i] == "" and remain_lines[i - 1] == "":
            remain_lines.pop(i)

    # split lines into chunk divided by empty line
    remain_chunks = [remain_lines[:]]
    while "" in remain_chunks[-1]:
        i = remain_chunks[-1].index("")
        remain = remain_chunks[-1][i + 1:]
        remain_chunks[-1] = remain_chunks[-1][:i]
        remain_chunks.append(remain)

    new_tasklist = "\n\n".join(
        ["\n".join([str(line) for line in chunk]) for chunk in remain_chunks])

    # output remain lines
    with open(task_path, "w", encoding="utf-8") as f:
        f.write(new_tasklist + "\n")
