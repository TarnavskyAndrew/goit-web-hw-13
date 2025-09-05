from enum import Enum
from fastapi import Depends, HTTPException, status
from src.services.auth import auth_service
from src.database.models import User


# Ролі користувачів
class Role(str, Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"


# Клас для перевірки ролей користувачів
class RoleAccess:

    def __init__(self, allowed: list[Role]):
        self.allowed = set(allowed)

    async def __call__(
        self, current_user: User = Depends(auth_service.get_current_user)
    ) -> User:
        if current_user.role not in self.allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )
        return current_user


# Залежності для перевірки ролей:
access_admin_only = RoleAccess([Role.admin])
access_admin_or_moderator = RoleAccess([Role.admin, Role.moderator])
