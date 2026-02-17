from fastapi  import status, HTTPException, APIRouter
from ..database import SessionDep
from .. import models, schemas, utils

router =  APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, session: SessionDep):
    hashed_pw = utils.hash_password(user.password)
    db_user = models.User(
        email=user.email,
        password=hashed_pw
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, session: SessionDep):
    user = session.get(models.User, id)
    if not user:
        raise HTTPException(status_code=404, detail="Post not found")
    return user