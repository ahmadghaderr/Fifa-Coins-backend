from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Header

SECRET_KEY = "secretfifakey"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_user_id(token: str = Header(...)):
    try:
        payload = decode_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
