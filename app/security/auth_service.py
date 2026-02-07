from app.security.password import verify_password, hash_password
from app.repository.local_repo import UserLocalRepo
from fastapi import HTTPException, status
from app.security.jwt import create_access_token

class AuthService:
    def __init__(self, repo: UserLocalRepo):
        self.repo = repo

    def login(self, email: str, password: str) -> dict:
        user = self.repo.get_user_by_email(email)
        if not user:
            print("User not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not verify_password(password, user.password):
            print("incorrect password")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect password")

        access_token = create_access_token(
            data={"sub": user.email}
        )
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
