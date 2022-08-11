import json
import os
import time
from datetime import datetime
from os.path import dirname, join

import requests
from dotenv import load_dotenv

ENV_AUTH = "CLICKUP_AUTH"
ENV_LIST = "CLICKUP_LIST"
ENV_TEMPLATE = "CLICKUP_TEMPLATE"

# list file of tasks
TASK_FILE = "tasks"

# timeout for single API run
TIMEOUT_SEC = 2

# maximum API run in a minute
POST_PER_MIN = 60

def post_template(title, auth, list_id, template_id):
    headers = {"Authorization": auth, "Content-Type": "application/json"}
    url = f"https://api.clickup.com/api/v2/list/{list_id}/taskTemplate/{template_id}"
    body = {"name": title}

    resp = requests.post(url, json=body, timeout=TIMEOUT_SEC, headers=headers)
    return resp


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

    remain_lines = [] # record failed task
    # post tasks
    for line in task_lines:
        # ignore blank line
        if line == "":
            remain_lines.append(line)
            continue

        # POST
        task = line
        print(f'Posting task "{task}"')
        start_micros = datetime.today().microsecond

        # try POST
        try:
            r = post_template(task, auth, list_id, template_id)
        except ReadTimeout:
            # when timeout
            r = None
            print(f"time out ({TIMEOUT_SEC} sec.)")
        else:
            # show result if not timeout
            print(f"{r.status_code}: {r.reason}")
        print("-" * 60)

        end_micros = datetime.today().microsecond

        if not (r is not None and r.status_code == 200):
            # record if fail
            remain_lines.add(task)

        elapsed_micros = end_micros - start_micros
        if elapsed_micros < INTERVAL_MICROS:
            # wait if POST end too fast
            waiting_micros = INTERVAL_MICROS - elapsed_micros
            if waiting_micros > 3000000:
                print(f"waiting {waiting_micros} microsec")
            time.sleep(waiting_micros / 1000000.0)

    # remove truncating ""
    while len(remain_lines) > 0 and remain_lines[-1] == "":
        remain_lines = remain_lines[:-1]
    # remove beggining ""
    while len(remain_lines) > 0 and remain_lines[0] == "":
        remain_lines = remain_lines[1:]
    # convert continuous "" into single ""
    print(remain_lines)  # DEBUG:
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
        ["\n".join([str(line) for line in chunk])
         for chunk in remain_chunks])

    # output remain lines
    with open(task_path, "w", encoding="utf-8") as f:
        f.write(new_tasklist)
