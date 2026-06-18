from decimal import getcontext
import requests
from datetime import datetime
from config.config import API_URL
import time
from crud.crud_functions import get_all_not_started_tasks, get_task_by_id
from dependencies import get_db
from .logic import encode


def process_tasks():
    while True:
        getcontext().prec = 14040
        db = next(get_db())
        not_started_tasks = get_all_not_started_tasks(db)

        if len(not_started_tasks) > 0:
            task_start = not_started_tasks[0]
            task_id = task_start.id
            task_start.start_time = datetime.now()
            task_start.status = "In progress"
            task_start.percentage = 0
            db.commit()
            db.close()

            get_response = requests.get(API_URL + f"gettaskcontent?task_id={task_id}")

            string = get_response.json()["string"]
            result = encode(string=string, task_id=task_id)

            body = {"task_id": task_id, "result": result}
            post_response = requests.post(API_URL + "sendresult", json=body)

            if post_response.json()["accepted"]:
                db = next(get_db())
                task_finish = get_task_by_id(db=db, task_id=task_id)
                if task_finish.status == "Cancelled":
                    continue
                task_finish.status = "Finished"
                task_finish.percentage = 100
                task_finish.finish_time = datetime.now()
                db.commit()
                db.close()
        else:
            db.close()
            time.sleep(2)
