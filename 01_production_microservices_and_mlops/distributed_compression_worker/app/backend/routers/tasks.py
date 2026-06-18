import json
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from starlette.responses import FileResponse
from auth.utils import get_current_user
from config.config import MAX_LENGTH
from crud.crud_functions import create_task, update_task_file_name, \
    get_all_user_not_started_tasks, delete_task_by_id, update_task_status, get_task_by_id
from dependencies import get_db
from logic.tasks_logic import get_user_tasks
from schemas.schemas import TaskForFrontend, TaskCreate

router = APIRouter()


@router.post("/createtask/")
async def create_task_endpoint(request: Request, body: TaskForFrontend, db: Session = Depends(get_db)):
    user = get_current_user(token=request.headers['Authorization'])

    if len(body.string) > int(MAX_LENGTH):
        return {"accepted": False}

    undone_user_tasks = get_all_user_not_started_tasks(db=db, user_id=user.id)
    if len(undone_user_tasks) >= 3:
        return {"accepted": False}

    task_create = TaskCreate(**{
        "user_id": user.id,
        "status": "Not started",
        "is_encode": body.is_encode,
        "length": len(body.string),
    })

    created_task = create_task(db=db, task_create=task_create)

    file_name = f"{created_task.id}.txt"

    try:
        with open("file_storage/" + file_name, "w") as file:
            for i in range(0, len(body.string), 1024):
                file.write(body.string[i:i+1024])
        update_task_file_name(db=db, task_id=created_task.id, file_name=file_name)
    except:
        delete_task_by_id(db=db, task_id=created_task.id)
        return {"accepted": False}

    return {"accepted": True}


@router.get("/gettasks/")
def get_tasks_endpoint(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(token=request.headers['Authorization'])

    return get_user_tasks(user_id=user.id, db=db)


@router.get("/gettaskcontent")
def get_tasks_content_endpoint(request: Request, task_id: int, db: Session = Depends(get_db)):
    task = get_task_by_id(db=db, task_id=task_id)
    with open("file_storage/" + task.file_name, "r") as file:
        string = file.read()
    return {"string": string}


@router.post("/sendresult")
async def accept_result_endpoint(request: Request, db: Session = Depends(get_db)):
    data = await request.json()

    task_id = data["task_id"]
    result_string = data["result"]

    task = get_task_by_id(db=db, task_id=task_id)
    with open("file_storage/" + task.file_name.split(".")[0] + "_result." + task.file_name.split(".")[1],
              "w") as file:
        file.write(json.dumps(result_string))

    return {"accepted": True}


@router.put("/canceltask")
def cancel_task_endpoint(request: Request, task_id: int, db: Session = Depends(get_db)):
    try:
        update_task_status(db=db, task_id=task_id, status="Cancelled")
    except:
        return {"is_cancelled": False}
    return {"is_cancelled": True}


@router.get("/downloadtask")
async def download_task_endpoint(request: Request, task_id: int, db: Session = Depends(get_db)):
    user = get_current_user(token=request.headers['Authorization'])
    task = get_task_by_id(db=db, task_id=task_id)

    if user.id == task.user_id:
        SAVE_FILE_PATH = f"file_storage/{task.id}_result.txt"
        new_filename = "result.txt"

        return FileResponse(
            path=SAVE_FILE_PATH,
            media_type="application/octet-stream",
            filename=new_filename,
        )
