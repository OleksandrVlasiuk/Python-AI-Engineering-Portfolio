from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    lang_preference: Mapped[str] = mapped_column(String(2), default="ua")
    is_light_theme: Mapped[bool] = mapped_column(Boolean, default=True)
    purchase_date: Mapped[datetime] = mapped_column(nullable=True)
    purchased_days: Mapped[int] = mapped_column(nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)


class Task(Base):
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(primary_key=True)

    start_time: Mapped[datetime] = mapped_column(nullable=True)
    finish_time: Mapped[datetime] = mapped_column(nullable=True)
    percentage: Mapped[int] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    is_encode: Mapped[bool] = mapped_column(Boolean, default=True)
    file_name: Mapped[str] = mapped_column(String(50), nullable=True)

    length: Mapped[int] = mapped_column(nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

