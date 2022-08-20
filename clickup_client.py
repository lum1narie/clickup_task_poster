import requests
import datetime
import time


class ClickUpClient():
    # timeout for single API run
    TIMEOUT_SEC = 2

    def __init__(self, auth, post_per_min=60):
        self.auth = auth
        self.set_post_per_min(post_per_min)
        self.last_accessed_time = datetime.datetime.now(
        ).microsecond - self.interval_micros

    def set_post_per_min(self, post_per_min):
        self.post_per_min = post_per_min
        self.interval_micros = 1000000.0 * 60.0 / self.post_per_min
        
    # FOLDER
    def get_folders(self, space_id, params=dict()):
        headers = {
            "Authorization": self.auth,
            "Content-Type": "application/json"
        }
        url = f"https://api.clickup.com/api/v2/space/{space_id}/folder"

        resp = self.access("GET", url, {
            "timeout": self.TIMEOUT_SEC,
            "headers": headers,
            "params": params
        })
        return resp

    # LIST
    def get_folderless_list(self, space_id, params=dict()):
        headers = {
            "Authorization": self.auth,
            "Content-Type": "application/json"
        }
        url = f"https://api.clickup.com/api/v2/space/{space_id}/list"

        resp = self.access("GET", url, {
            "timeout": self.TIMEOUT_SEC,
            "headers": headers,
            "params": params
        })
        return resp

    # TASK
    def get_tasks(self, list_id, params=dict()):
        headers = {
            "Authorization": self.auth,
            "Content-Type": "application/json"
        }
        url = f"https://api.clickup.com/api/v2/list/{list_id}/task"

        resp = self.access("GET", url, {
            "timeout": self.TIMEOUT_SEC,
            "headers": headers,
            "params": params
        })
        return resp

    def create_task_template(self, body, list_id, template_id):
        headers = {
            "Authorization": self.auth,
            "Content-Type": "application/json"
        }
        url = f"https://api.clickup.com/api/v2/list/{list_id}/taskTemplate/{template_id}"

        resp = self.access("POST", url, {
            "timeout": self.TIMEOUT_SEC,
            "headers": headers,
            "json": body
        })
        return resp


    def access(self, method, url, args):
        PRINT_MICROS_THRESHOLD = 3000000
        elapsed_micros = datetime.datetime.now(
        ).microsecond - self.last_accessed_time
        if elapsed_micros < self.interval_micros:
            # wait if it is too less time from last access
            wait_micros = self.interval_micros - elapsed_micros
            if wait_micros > PRINT_MICROS_THRESHOLD:
                print(f"waiting {wait_micros} microsec")
            wait_sec = wait_micros / 1000000.0
            time.sleep(wait_sec)

        # access
        try:
            r = requests.request(method, url, **args)
        except requests.ReadTimeout:
            # when timeout
            r = None
        self.last_accessed_time = datetime.datetime.now().microsecond

        return r
