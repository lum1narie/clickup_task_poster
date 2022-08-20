import os
from os.path import dirname, join
import datetime

from clickup_client import *
from clickup_utility import *

from dotenv import load_dotenv

ENV_AUTH = "CLICKUP_AUTH"
ENV_SPACE = "CLICKUP_SPACE"

# maximum API run in a minute
POST_PER_MIN = 60

if __name__ == "__main__":
    # load dotenv
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    auth = os.environ.get(ENV_AUTH)
    space_id = os.environ.get(ENV_SPACE)

    c = ClickUpClient(auth, POST_PER_MIN)

    d = int(datetime.datetime.strptime('20220801',
                                       '%Y%m%d').timestamp()) * 1000
    task_param = {
        "archived": True,
        "order_by": "created",
        "subtasks": True,
        "include_closed": True,
        "date_created_gt": d
    }
    tasks = get_all_tasks(c,
                          space_id,
                          list_param={"archived": True},
                          task_param=task_param)
    print("\n".join(map(str, tasks)))
