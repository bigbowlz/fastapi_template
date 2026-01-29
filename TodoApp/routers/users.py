import os
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from models import Users
from starlette import status
from .auth import get_current_user, get_db
from passlib.context import CryptContext

router = APIRouter(prefix="/users", tags=["users"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

secret_key = os.getenv("SECRET_KEY")
algo = os.getenv("ALGORITHM")

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class UserPasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


@router.get("/user")
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )
    return db.query(Users).filter(Users.id == user.get("user_id")).first()


@router.post("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    new_password_request: UserPasswordChangeRequest,
    user: user_dependency,
    db: db_dependency,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )
    user_model = db.query(Users).filter(Users.id == user.get("user_id")).first()
    if not bcrypt_context.verify(
        new_password_request.old_password, user_model.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Cannot verify password."
        )
    user_model.hashed_password = bcrypt_context.hash(new_password_request.new_password)
    db.add(user_model)
    db.commit()
