import time
time.sleep(30)
from crud.crud_functions import create_user, create_task, update_task_file_name
from dependencies import get_db
from schemas.schemas import TaskCreate, UserAuthBackend
from worker.worker import process_tasks


# new_user = UserAuthBackend(**{
#     "name": "TEST",
#     "email": "test@test.test",
#     'hashed_password': "$b$gfjdgglslgk",
#     "is_verified": True
# })
# created_user = create_user(db=next(get_db()), user_create=new_user)
#
# task_create = TaskCreate(**{
#     "user_id": created_user.id,
#     "status": "Not started",
#     "is_encode": True,
#     "length": 3000,
# })
#
# created_task = create_task(db=next(get_db()), task_create=task_create)
# update_task_file_name(db=next(get_db()), task_id=created_task.id, file_name="TEST.txt")
#
# created_task = create_task(db=next(get_db()), task_create=task_create)
# update_task_file_name(db=next(get_db()), task_id=created_task.id, file_name="TEST.txt")
#
# created_task = create_task(db=next(get_db()), task_create=task_create)
# update_task_file_name(db=next(get_db()), task_id=created_task.id, file_name="TEST.txt")


process_tasks()
