from fastapi import FastAPI, HTTPException
from app.security import password, jwt, dependecies, auth_service
from typing import List
from app.dto.user_dto import UserDTO
from app.exception.exceptions import UserNotFound, UserAlreadyExists, GeneralError
from app.repository.local_repo import UserLocalRepo
from app.schemas.user_schema import APIResponse
from app.service.user_service import UserService
from app.security.password import hash_password
from app.security.auth_service import AuthService

app = FastAPI()

hashed_password = hash_password("12345678")

# seed data
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

repo = UserLocalRepo(seed_users)
auth_service = AuthService(repo)
service = UserService(repo)


@app.get("/users", response_model=APIResponse)
def get_users():
    try:
        users = service.list_users()
        return APIResponse(status=200, message="OK", data={"users": users})
    except Exception as e:
        # Real server error
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/users", response_model=APIResponse)
def create_users(user: UserDTO):
    try:
        created_user = service.create_user(user)
        return APIResponse(status=201, message="OK", data={"userData": created_user})
    except UserAlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))
    except GeneralError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/users/{user_id}", response_model=APIResponse)
def delete_user(user_id: int):
    try:
        service.delete_user(user_id)
        return APIResponse(status=200, message="OK", data={"message": "user deleted"})
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/users/{user_id}", response_model=APIResponse)
def update_user_name(user_id: int, name: str):
    try:
        updated_user = service.update_user_name(user_id, name)
        return APIResponse(status=200, message="OK", data={"userData": updated_user})
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except GeneralError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# AUTH SERVICE
@app.post("/auth/login", response_model=APIResponse)
def login(email: str, password: str):
    dict = auth_service.login(email, password)  # returns user DTO
    return APIResponse(
        status=200,
        message="Login successful",
        data= dict
    )
