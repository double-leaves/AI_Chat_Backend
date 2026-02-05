from fastapi import FastAPI, Depends
from sqlmodel import Session
from models import ChatMessageCreate, ChatMessageRead, ChatMessage, ChatSessionRead, ChatSessionCreate, ChatSession
from database import get_session, create_db_and_tables
import time


app = FastAPI()


# 模拟 AI
def fake_ai_response(content: str) -> str:
    time.sleep(1)  # 假装在思考
    return f"AI回复: {content}"

create_db_and_tables()


@app.post("/chats/", response_model=ChatSessionRead)
def create_session(session_in: ChatSessionCreate, session: Session = Depends(get_session)):
    session_db = ChatSession.model_validate(session_in)
    session.add(session_db)
    session.commit()
    session.refresh(session_db)
    return session_db


@app.post("/chats/{session_id}/messages/", response_model=ChatMessageRead)
def create_message(
        session_id: int,
        message_in: ChatMessageCreate,
        session: Session = Depends(get_session)
):
    # --- 你的任务区域开始 ---

    # 第一步：把用户说的话 (message_in.content) 变成数据库对象
    # 注意：你需要手动填上 session_id 和 judge="user"
    message_db = ChatMessage(
        session_id=session_id,
        content=message_in.content,
        judge="user"
    )
    # 第二步：保存用户消息到数据库 (add, commit, refresh)
    session.add(message_db)
    session.commit()
    session.refresh(message_db)
    # 第三步：调用假 AI 获取回复
    ai_content = fake_ai_response(message_in.content)
    # 第四步：把 AI 的回复变成数据库对象
    # 注意：session_id 是一样的，但 judge="ai"
    ai_message_db = ChatMessage(
        session_id=session_id,
        content=ai_content,
        judge="ai"
    )
    # 第五步：保存 AI 消息到数据库
    session.add(ai_message_db)
    session.commit()
    session.refresh(ai_message_db)
    # 第六步：返回 AI 的那条消息对象 (让前端显示)
    return ai_message_db
    # --- 你的任务区域结束 ---

