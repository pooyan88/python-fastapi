from dataclasses import dataclass
from typing import List, Optional
from app.dto.user_dto import UserDTO
from app.repository.local_repo import UserLocalRepo


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]


class UserValidationRules:
    def __init__(self, repo: UserLocalRepo):
        self.repo = repo

    def validate_create(self, user: UserDTO) -> ValidationResult:
        errors: List[str] = []

        if not user.username or not user.username.strip():
            errors.append("username is required")

        if not user.email or not user.email.strip():
            errors.append("email is required")
        elif "@" not in user.email:
            errors.append("email is not valid")

        if not user.password or len(user.password) < 8:
            errors.append("password must be at least 8 characters")
        elif len(user.password) > 72:
            errors.append("password cannot be longer than 72 characters")

        return ValidationResult(is_valid=(len(errors) == 0), errors=errors)