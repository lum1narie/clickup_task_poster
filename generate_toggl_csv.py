import os
import sys  # DEBUG:
from os.path import dirname, join
import datetime
import csv

from clickup_client import *
from clickup_utility import *

from dotenv import load_dotenv

ENV_AUTH = "CLICKUP_AUTH"
ENV_TEAM = "CLICKUP_TEAM"
ENV_SPACE = "CLICKUP_SPACE"
ENV_EMAIL = "TOGGL_EMAIL"
ENV_USER = "TOGGL_USER"
ENV_START_DATE = "TIMER_START_DATE"

# maximum API run in a minute
POST_PER_MIN = 60


def generate_toggl_csv(client, space_id, times, user, email, out_path):
    header = [
        "User", "Email", "Project", "Description", "Start date", "Start time",
        "Duration", "Tags"
    ]
    i = 1  # DEBUG:
    t_n = len(times)  # DEBUG:

    with open(out_path, "w", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        f.flush()

        for t in times:
            data = ["" for _ in range(len(header))]

            start_ms = int(t["start"])
            end_ms = int(t["end"])

            delta_total_sec = (end_ms - start_ms) // 1000
            delta_sec = delta_total_sec % 60
            delta_min = (delta_total_sec // 60) % 60
            delta_hour = delta_total_sec // 3600

            list_id = t["task_location"]["list_id"]
            if "list_name" in t["task_location"]:
                list_name = t["task_location"]["list_name"]
            else:
                list_name = ""

            data[0] = user
            data[1] = email
            data[2] = list_name
            data[3] = t["task"]["name"]
            data[4] = datetime.datetime.fromtimestamp(
                start_ms // 1000).strftime('%Y-%m-%d')
            data[5] = datetime.datetime.fromtimestamp(
                start_ms // 1000).strftime('%H:%M:%S')
            data[6] = "{:02d}:{:02d}:{:02d}".format(delta_hour, delta_min,
                                                    delta_sec)
            data[7] = ",".join(sorted([tg["name"] for tg in t["task_tags"]]))

            w.writerow(data)
            f.flush()

            print(f'{i} / {t_n}', file=sys.stderr)  # DEBUG:
            i += 1  # DEBUG:


if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_dt = datetime.datetime.strptime(sys.argv[1], '%Y%m%d%H%M')
    else:
        start_dt = datetime.datetime.now() - datetime.timedelta(days = 7)

    # load dotenv
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    auth = os.environ.get(ENV_AUTH)
    team_id = os.environ.get(ENV_TEAM)
    space_id = os.environ.get(ENV_SPACE)
    email = os.environ.get(ENV_EMAIL)
    user = os.environ.get(ENV_USER)


    c = ClickUpClient(auth, POST_PER_MIN)

    d = int(start_dt.timestamp() * 1000)
    time_params = {
        "start_date": d,
        "end_date": int(datetime.datetime.now().timestamp() * 1000),
        "include_task_tags": "true",
        "include_location_names": "true"
    }

    times = c.get_time_entries_in_range(team_id, time_params).json()["data"]

    filename = f"toggl_{start_dt.strftime('%Y%m%d%H%M')}.csv"
    generate_toggl_csv(c, space_id, times, user, email, filename)
