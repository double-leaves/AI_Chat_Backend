from sqlmodel import Session, create_engine, SQLModel


# 配置数据库url
file_name = "chat_library"
file_url = f"sqlite:///{file_name}"

# 引擎
engine = create_engine(file_url)


# 创建引擎
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# 依赖注入
def get_session():
    with Session(engine) as session:
        yield session
