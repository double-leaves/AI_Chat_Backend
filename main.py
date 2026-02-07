from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from models import ChatMessageCreate, ChatMessageRead, ChatMessage, ChatSessionRead, ChatSessionCreate, ChatSession, \
    UserRead, UserCreate, User
from database import get_session, create_db_and_tables
from security import get_password_hash, verify_password, create_access_token, get_current_user
from typing import List
import time


app = FastAPI()


# 模拟 AI
def fake_ai_response(content: str) -> str:
    time.sleep(1)  # 假装在思考
    return f"AI回复: {content}"


create_db_and_tables()


# 用户注册
@app.post("/register/", response_model=UserRead)
def create_user(
    user_in: UserCreate,
    session=Depends(get_session)
):
    user = User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


# 用户登录
# 注意：这个接口不返回 UserRead，而是返回一个包含 token 的特定字典
@app.post("/token")
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)
):
    # form_data 里面包含了 form_data.username 和 form_data.password

    # 第一步：去数据库找人 (Query)
    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",  # 模糊的错误提示更安全
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 发手环 (Create Token)
    access_token = create_access_token(data={"sub": user.username})
    # 返回标准格式
    return {"access_token": access_token, "token_type": "bearer"}


# 创建新会话
@app.post("/chats/", response_model=ChatSessionRead)
def create_session(
        session_in: ChatSessionCreate,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    session_db = ChatSession.model_validate(session_in)
    session_db.user_id = current_user.id
    session.add(session_db)
    session.commit()
    session.refresh(session_db)
    return session_db


# 人机对话
@app.post("/chats/{session_id}/messages/", response_model=ChatMessageRead)
def create_message(
        session_id: int,
        message_in: ChatMessageCreate,
        # 1. 注入当前用户 (安检)
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    # 2. 先检查这个会话是否存在，以及是否属于当前用户
    statement = select(ChatSession).where(ChatSession.id == session_id)
    chat_session = session.exec(statement).first()

    # 情况 A: 会话根本不存在
    if not chat_session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 情况 B: 会话存在，但不是你的 (越权警报!)
    if chat_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="你没有权限操作此会话")

    # --- 验证通过，下面才是正常的业务逻辑 ---

    # 第一步：保存用户消息
    message_db = ChatMessage(
        session_id=session_id,
        content=message_in.content,
        judge="user"
    )
    session.add(message_db)
    session.commit()
    session.refresh(message_db)

    # 第二步：调用 AI (模拟)
    ai_content = fake_ai_response(message_in.content)

    # 第三步：保存 AI 消息
    ai_message_db = ChatMessage(
        session_id=session_id,
        content=ai_content,
        judge="ai"
    )
    session.add(ai_message_db)
    session.commit()
    session.refresh(ai_message_db)

    return ai_message_db


# 获取当前用户会话
@app.get("/chats", response_model=List[ChatSessionRead])
def read_sessions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(ChatSession).where(ChatSession.user_id == current_user.id)
    results = session.exec(statement).all()

    return results


# 获取消息
@app.get("/chats/{session_id}/messages", response_model=List[ChatMessageRead])
def read_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    chat_session = session.exec(select(ChatSession).where(ChatSession.id == session_id)).first()
    if not chat_session or chat_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    statement = select(ChatMessage).where(ChatMessage.session_id == session_id)
    results = session.exec(statement).all()

    return results
