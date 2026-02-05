from typing import Optional
from sqlmodel import SQLModel, Field


# 用户
class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)  # 密码长度限制


class UserRead(UserBase):
    id: int


# 会话表
class ChatSessionBase(SQLModel):
    title: str


class ChatSession(ChatSessionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionRead(ChatSessionBase):
    id: int
    user_id: int


# 消息表
class ChatMessageBase(SQLModel):
    content: str


class ChatMessage(ChatMessageBase, table=True):
    id: int = Field(default=None, primary_key=True)
    session_id: Optional[int] = Field(default=None, foreign_key="chatsession.id")
    judge: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageRead(ChatMessageBase):
    id: int
    judge: str
