from sqlalchemy.orm import Session
from config.config import TIME_BY_LENGTH
from crud.crud_functions import get_all_not_started_or_in_progress_tasks, get_tasks_by_user_id


def get_time_by_length(length):
    for key, value in TIME_BY_LENGTH.items():
        if length <= key and length + 500 > key:
            return value
    return 0


def get_user_tasks(user_id: int, db: Session):
    user_tasks = get_tasks_by_user_id(db=db, user_id=user_id)

    for i in range(len(user_tasks)):
        if user_tasks[i].start_time is not None:
            user_tasks[i].start_time = user_tasks[i].start_time.strftime("%Y-%m-%d %H:%M:%S")
        if user_tasks[i].finish_time is not None:
            user_tasks[i].finish_time = user_tasks[i].finish_time.strftime("%Y-%m-%d %H:%M:%S")

        if user_tasks[i].status == "In progress":
            user_tasks[i].status += f" ({user_tasks[i].percentage if user_tasks[i].percentage is not None else '0'}%)"
        if user_tasks[i].status == "Not started":
            all_tasks = get_all_not_started_or_in_progress_tasks(db=db)

            estimate_time = get_aproxiamet_time(workers_count=3, tasks=all_tasks, task_id=user_tasks[i].id)
            user_tasks[i].status += f" (starts in {int(estimate_time)}s.)"
    user_tasks.reverse()

    return user_tasks


def get_aproxiamet_time(tasks, task_id, workers_count=3):
    workers_time = [0] * workers_count
    for task in tasks:
        if task.id >= task_id:
            break
        free_worker = min(workers_time)
        indx = workers_time.index(free_worker)
        if task.status.startswith("In progress"):
            workers_time[indx] += (100 - task.percentage) / 100 * get_time_by_length(task.length)
        else:
            workers_time[indx] += get_time_by_length(task.length)
    return min(workers_time)
