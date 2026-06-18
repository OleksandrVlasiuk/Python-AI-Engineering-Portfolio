from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from crud.crud_functions import get_user_by_email
from dependencies import get_db
from schemas.schemas import TokenSchema, LoginData
from . import utils


router = APIRouter()


@router.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):  # form_data: OAuth2PasswordRequestForm = Depends(),
    user = get_user_by_email(email=form_data.username, db=db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user.hashed_password
    if not utils.verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is not verified"
        )

    return {
        "access_token": utils.create_access_token(user.id),
        "refresh_token": utils.create_refresh_token(user.id),
    }

