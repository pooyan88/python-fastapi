from typing import List
from app.dto.user_dto import UserDTO
from app.exception.exceptions import UserNotFound, UserAlreadyExists, GeneralError
from app.repository.local_repo import UserLocalRepo
from app.security.password import hash_password


class UserService:
    def __init__(self, user_repo: UserLocalRepo):
        self.user_repo = user_repo

    def _validate_create(self, user: UserDTO) -> None:
        if not user.username or not user.username.strip():
            raise GeneralError("username is required")

        if not user.email or not user.email.strip():
            raise GeneralError("email is required")

        if "@" not in user.email:
            raise GeneralError("email is not valid")

        # Uniqueness checks (recommended)
        # If your repo doesn't have these methods yet, see fallback below.
        if hasattr(self.user_repo, "get_user_by_username"):
            if self.user_repo.get_user_by_username(user.username) is not None:
                raise UserAlreadyExists("username already exists")

        if hasattr(self.user_repo, "get_user_by_email"):
            if self.user_repo.get_user_by_email(user.email) is not None:
                raise UserAlreadyExists("email already exists")

        # Also avoid duplicated ID (if your repo add_user checks it, this is optional)
        if self.user_repo.get_user_by_id(user.id) is not None:
            raise UserAlreadyExists("user with this id already exists")

    def _validate_update_names(self, first_name: str, last_name: str) -> None:
        if first_name is not None and len(first_name.strip()) == 0:
            raise GeneralError("first_name cannot be empty")
        if last_name is not None and len(last_name.strip()) == 0:
            raise GeneralError("last_name cannot be empty")

    # -------------------------
    # CRUD
    # -------------------------
    def list_users(self) -> List[UserDTO]:
        return self.user_repo.get_all_users()

    def get_user(self, user_id: int) -> UserDTO:
        user = self.user_repo.get_user_by_id(user_id)
        if user is None:
            raise UserNotFound(f"user {user_id} not found")
        return user

    def create_user(self, user: UserDTO) -> UserDTO:
        self._validate_create(user)
        user.password = hash_password(user.password)
        added = self.user_repo.add_user(user)
        if not added:
            # repo said it couldn't add; treat as duplicate
            raise UserAlreadyExists("user already exists")

        return user

    def delete_user(self, user_id: int) -> None:
        removed = self.user_repo.remove_user(user_id)
        if not removed:
            raise UserNotFound(f"user {user_id} not found")

    def update_user_name(self, user_id: int, new_name: str) -> UserDTO:
        if not new_name or not new_name.strip():
            raise GeneralError("name is required")

        user = self.user_repo.get_user_by_id(user_id)
        if user is None:
            raise UserNotFound(f"user {user_id} not found")

        user.first_name = new_name
        # If you later add repo.update_user(user), call it here.
        return user