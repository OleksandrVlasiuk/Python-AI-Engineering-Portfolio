from uuid import UUID
from pydantic import BaseModel


class TaskForFrontend(BaseModel):
    string: str
    is_encode: bool


class TaskCreate(BaseModel):
    user_id: int
    status: str
    is_encode: bool
    length: int


# AUTH
class VerificationToken(BaseModel):
    token: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class UserAuth(BaseModel):
    name: str
    email: str
    password: str


class UserAuthBackend(BaseModel):
    name: str
    email: str
    hashed_password: str
    is_verified: bool


class UserOut(BaseModel):
    id: UUID
    email: str


class SystemUser(UserOut):
    password: str


class LoginData:
    email: str
    password: str
