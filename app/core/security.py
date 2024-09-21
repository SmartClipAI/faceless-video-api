from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.core.config import settings
import bcrypt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")

class TokenData(BaseModel):
    username: str | None = None

def get_password_hash(password: str) -> str:
    password_byte_enc = password.encode()
    hashed_password = bcrypt.hashpw(password_byte_enc, bcrypt.gensalt())
    return hashed_password.decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode()
    hashed_password_bytes = hashed_password.encode()
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_bytes)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    from app.models.user import User
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await User.get_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt