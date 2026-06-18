from pydantic import BaseModel


class TaskCreate(BaseModel):
    user_id: int
    status: str
    is_encode: bool
    length: int


class UserAuthBackend(BaseModel):
    name: str
    email: str
    hashed_password: str
    is_verified: bool
