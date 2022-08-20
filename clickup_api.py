import requests

# timeout for single API run
TIMEOUT_SEC = 2


def create_task_template(body, auth, list_id, template_id):
    headers = {"Authorization": auth, "Content-Type": "application/json"}
    url = f"https://api.clickup.com/api/v2/list/{list_id}/taskTemplate/{template_id}"

    resp = requests.post(url, json=body, timeout=TIMEOUT_SEC, headers=headers)
    return resp
