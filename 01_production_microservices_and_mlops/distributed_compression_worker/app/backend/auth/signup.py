from fastapi import status, HTTPException, APIRouter, Depends, Request
from sqlalchemy.orm import Session
from crud.crud_functions import get_user_by_email, create_user, verify_user
from dependencies import get_db
from logic.send_mail import send_mail
from schemas.schemas import UserAuth, UserAuthBackend, VerificationToken
from . import utils
from .utils import get_user_by_verification_token

router = APIRouter()


@router.post('/signup', summary="Create new user")
async def create_user_endpoint(data: UserAuth, db: Session = Depends(get_db)):

    user = get_user_by_email(email=data.email, db=db)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )

    user_create = UserAuthBackend(
        **{"name": data.name, "email": data.email, 'hashed_password': utils.get_hashed_password(data.password), "is_verified": False})
    created_user = create_user(db=db, user_create=user_create)

    send_mail(data.email)

    return created_user


@router.post('/verification')
async def verify_email_endpoint(body: VerificationToken, db: Session = Depends(get_db)):
    user = get_user_by_verification_token(token=body.token)

    verify_user(user_id=user.id, db=db)

    # return {
    #     "access_token": utils.create_access_token(user.id),
    #     "refresh_token": utils.create_refresh_token(user.id),
    # }
    return {"verified": True}

