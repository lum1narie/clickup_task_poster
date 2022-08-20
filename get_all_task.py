import os
from os.path import dirname, join

from clickup_client import *

from dotenv import load_dotenv

ENV_AUTH = "CLICKUP_AUTH"
ENV_SPACE = "CLICKUP_SPACE"

# maximum API run in a minute
POST_PER_MIN = 60


def get_all_lists(client, space_id, params=dict()):
    lists = []

    resp = c.get_folderless_list(space_id, params)
    lists += resp.json()["lists"]

    resp = c.get_folders(space_id, params)
    folder = resp.json()["folders"]
    lists += sum([f["lists"] for f in folder], [])

    return lists


def get_all_tasks_in_list(client, list_id, params=dict()):
    tasks = []
    page = 0
    params["subtasks"] = True

    while True:
        params["page"] = page
        resp = client.get_tasks(list_id, params)
        if "tasks" not in resp.json():
            print(resp.json())
            break

        tasks += resp.json()["tasks"]
        if len(resp.json()["tasks"]) != 100:
            break

        page += 1

    return tasks


def get_all_tasks(client, space_id, list_param=dict(), task_param=dict()):
    lists = get_all_lists(client, space_id, list_param)

    tasks = []
    for l in lists:
        tasks += get_all_tasks_in_list(client, l["id"], task_param)

    return tasks


if __name__ == "__main__":
    # load dotenv
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    auth = os.environ.get(ENV_AUTH)
    space_id = os.environ.get(ENV_SPACE)

    c = ClickUpClient(auth, POST_PER_MIN)

    tasks = get_all_tasks(c,
                          space_id,
                          list_param={"archived": True},
                          task_param={
                              "archived": True,
                              "order_by": "created",
                              "subtasks": True,
                              "include_closed": True,
                          })
    print("\n".join(map(str, tasks)))
