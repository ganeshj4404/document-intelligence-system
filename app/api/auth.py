import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer

from app.database import get_user_by_username
from app.services.auth_service import (
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Find user in the database
    user = get_user_by_username(form_data.username)

    # Check username
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Check password
    password_is_valid = verify_password(
        form_data.password,
        user["password_hash"],
    )

    if not password_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create JWT token
    access_token = create_access_token(user["username"])

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = get_user_by_username(username)

    if user is None:
        raise credentials_exception

    return user