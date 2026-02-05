from typing import Optional
from sqlmodel import SQLModel, Field


# 用户
class UserBase(SQLModel):
    username: str


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=24)  # 密码长度限制


class UserData(UserBase):
    id: Optional[int] = Field(default=None, primary_key=True)


class UserRead(UserBase):
    id: Optional[int] = Field(default=None, primary_key=True)




