from datetime import datetime, timedelta
from typing import Union
import jwt
from passlib.context import CryptContext


#  配置
SECRET_KEY = "你自己随便写一串复杂的乱码"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 密码哈希
def get_password_hash(secret: str):
    return


def verify_password(secret: str, hashed: str):
    if get_password_hash(secret) == hashed:
        return True
    return False

# JWT制造
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()

    end_time = datetime.now() + expires_delta

    to_encode["exp"] = end_time

    encoded_jwt = jwt.encode()

    return encoded_jwt