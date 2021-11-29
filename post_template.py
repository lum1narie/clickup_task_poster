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

TASK_FILE = "tasks"

TIMEOUT_SEC = 2


def post_template(title, auth, list_id, template_id):
    headers = {"Authorization": auth, "Content-Type": "application/json"}
    url = f"https://api.clickup.com/api/v2/list/{list_id}/taskTemplate/{template_id}"
    body = {"name": title}

    resp = requests.post(url, json=body, timeout=TIMEOUT_SEC, headers=headers)
    return resp


if __name__ == "__main__":
    POST_PER_MIN = 60
    INTERVAL_MICROS = 1000000.0 * 60.0 / POST_PER_MIN

    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    auth = os.environ.get(ENV_AUTH)
    list_id = os.environ.get(ENV_LIST)
    template_id = os.environ.get(ENV_TEMPLATE)

    task_path = join(dirname(__file__), TASK_FILE)
    tasks_lines = []
    posted_tasks = set()
    with open(task_path, "r", encoding="utf-8") as f:
        tasks_lines = f.read().splitlines()
    tasks = set(tasks_lines)

    for task in tasks:
        print(f'Posting task "{task}"')
        start_micros = datetime.today().microsecond

        try:
            r = post_template(task, auth, list_id, template_id)
        except ReadTimeout:
            print(f"time out ({TIMEOUT_SEC} sec.)")
        else:
            r = None
            print(f"{r.status_code}: {r.reason}")
        print("-" * 60)

        end_micros = datetime.today().microsecond

        if r is not None and r.status_code == 200:
            elapsed_micros = end_micros - start_micros
            if elapsed_micros < INTERVAL_MICROS:
                waiting_micros = INTERVAL_MICROS - elapsed_micros
                if waiting_micros > 3000000:
                    print(f"waiting {waiting_micros} microsec")
                time.sleep(waiting_micros / 1000000.0)

            posted_tasks.add(task)

    new_tasklist = "\n".join([str(task) for task in tasks - posted_tasks])
    with open(task_path, "w", encoding="utf-8") as f:
        f.write(new_tasklist)
