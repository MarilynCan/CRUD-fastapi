from fastapi  import Depends, HTTPException, APIRouter, status
from ..database import SessionDep
from typing import Annotated
from .. import models, schemas, utils, oauth2
from sqlmodel import select
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(tags=['Authentication'])

@router.post("/login", response_model=schemas.Token)
def login(session: SessionDep, user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()]):
    
    # {
    #     "username": "fnsf",
    #     "password": "gdsgsg"
    # }

    user = session.exec(
        select(models.User).where(models.User.email == user_credentials.username)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create a token
    # Return token
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}