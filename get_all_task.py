import os
import sys
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

    task_param = {
        "archived": "true",
        "order_by": "created",
        "subtasks": "true",
        "include_closed": "true",
    }
    tasks = get_all_tasks(c,
                          space_id,
                          list_param={"archived": "true"},
                          task_param=task_param)
    print("\n".join(map(str, tasks)))

    print(f"{c.access_count} times accessed API", file=sys.stderr)
    
