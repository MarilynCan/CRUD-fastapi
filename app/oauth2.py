from datetime import datetime, timedelta, timezone
import jwt
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from sqlmodel import  Session, select
from .config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')
SessionDep = Annotated[Session, Depends(database.get_session)]

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:          
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      id: str = payload.get("user_id")
      if id is None:
          raise credentials_exception
      token_data = schemas.TokenData(id=id)
    except InvalidTokenError:
        raise credentials_exception
    return token_data
    

def get_current_user(
    db: SessionDep,
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)

    user = db.exec(
        select(models.User).where(models.User.id == token_data.id)
    ).first()

    if not user:
        raise credentials_exception

    return user
        