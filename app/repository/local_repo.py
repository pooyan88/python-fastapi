from typing import List, Optional
from app.dto.user_dto import UserDTO

class UserLocalRepo:
    def __init__(self, users: Optional[List[UserDTO]] = None):
        self.users: List[UserDTO] = users if users is not None else []

    def get_all_users(self) -> List[UserDTO]:
        return self.users

    def is_user_exists(self, target: UserDTO) -> bool:
        for user in self.users:
            if user.id == target.id:
                return True
        return False  # <-- moved outside loop

    def get_user_by_id(self, user_id: int) -> Optional[UserDTO]:
        for user in self.users:
            if user.id == user_id:
                return user
        return None  # <-- moved outside loop

    def get_user_by_email(self, email: str) -> Optional[UserDTO]:
        for user in self.users:
            if user.email == email:
                return  user
        return  None

    def add_user(self, user: UserDTO) -> bool:
        if self.is_user_exists(user):
            return False  # duplicated user
        self.users.append(user)
        return True

    def remove_user(self, user_id: int) -> bool:
        before = len(self.users)
        self.users = [u for u in self.users if u.id != user_id]
        return len(self.users) < before

    def update_user_name(self, user_id: int, new_name: str) -> bool:
        for user in self.users:
            if user.id == user_id:
                user.name = new_name
                return True
        return False