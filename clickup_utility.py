def get_all_lists(client, space_id, params=dict()):
    lists = []

    for opt in ["true", "false"]:
        params["archived"] = opt
        resp = client.get_folderless_list(space_id, params)
        lists += resp.json()["lists"]

        resp = client.get_folders(space_id, params)
        folder = resp.json()["folders"]
        lists += sum([f["lists"] for f in folder], [])

    return lists


def get_all_tasks_in_list(client, list_id, params=dict()):
    tasks = []
    page = 0
    params["subtasks"] = "true"


    for opt in ["true", "false"]:
        params["archived"] = opt
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
