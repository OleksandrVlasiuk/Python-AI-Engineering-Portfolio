from fastapi import APIRouter, Request
from . import utils
from .utils import get_user_by_refresh_token


router = APIRouter()

@router.post('/refresh')
async def refresh(request: Request):
    res = await request.json()

    user = get_user_by_refresh_token(res["refresh_token"])
    new_access_token = utils.create_access_token(user.id)

    return {"access_token": new_access_token}
