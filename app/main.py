from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import List
from app.dto.user_dto import UserDTO
from app.exception.exceptions import UserNotFound, UserAlreadyExists, GeneralError
from app.repository.local_repo import UserLocalRepo
from app.schemas.user_schema import APIResponse
from app.service.user_service import UserService
from app.security.password import hash_password, verify_password
from app.security.auth_service import AuthService
from app.security.jwt import create_access_token, decode_token
from app.core.config import SECRET_KEY

app = FastAPI()

# -----------------------------
# Seed data
# -----------------------------
hashed_password = hash_password("12345678")

seed_users: List[UserDTO] = [
    UserDTO(
        id=1,
        email="ali@google.com",
        username="alireza",
        first_name="Alireza",
        last_name="rezaei",
        password=hashed_password
    )
]

# -----------------------------
# Repos and services
# -----------------------------
repo = UserLocalRepo(seed_users)
service = UserService(repo)
auth_service = AuthService(repo)

# -----------------------------
# JWT / OAuth2
# -----------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decode token, find user from repo, return user DTO
    """
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = repo.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

# -----------------------------
# USER ROUTES
# -----------------------------
@app.get("/users", response_model=APIResponse)
def get_users(current_user: UserDTO = Depends(get_current_user)):
    return APIResponse(status=200, message="OK", data={"users": service.list_users()})


@app.post("/users", response_model=APIResponse)
def create_users(user: UserDTO):
    try:
        created_user = service.create_user(user)
        return APIResponse(status=201, message="User created", data={"userData": created_user})
    except UserAlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))
    except GeneralError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/users/{user_id}", response_model=APIResponse)
def delete_user(user_id: int):
    try:
        service.delete_user(user_id)
        return APIResponse(status=200, message="User deleted", data={"message": "user deleted"})
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/users/{user_id}", response_model=APIResponse)
def update_user_name(user_id: int, name: str):
    try:
        updated_user = service.update_user_name(user_id, name)
        return APIResponse(status=200, message="User updated", data={"userData": updated_user})
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except GeneralError as e:
        raise HTTPException(status_code=400, detail=str(e))

# -----------------------------
# AUTH ROUTE
# -----------------------------
@app.post("/auth/login", response_model=APIResponse)
def login(email: str, password: str):
    user = repo.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect password")

    # Create JWT token
    access_token = create_access_token({"sub": user.email})
    return APIResponse(
        status=200,
        message=f"Login successful for user {user.username}",
        data={"access_token": access_token, "token_type": "bearer"}
    )
