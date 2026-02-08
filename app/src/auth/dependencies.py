from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi import Request, Depends
from utils import Tokens
from db.redis import token_in_block_list
from db.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from auth.service import UserService
from typing import List
from db.models import User
from errors import (
    InvalidTokenException,
    RefreshTokenRequiredException,
    AccessTokenRequiredException,
    InsufficientPermissionException,
    AccountNotVerifiedException,
    UserNotFoundException,
)


user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = Tokens.decode_token(token)

        if token_data is None:
            raise InvalidTokenException()

        if await token_in_block_list(token_data["jti"]):

            raise InvalidTokenException()

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = Tokens.decode_token(token)

        return token_data is not None

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequiredException()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequiredException()


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]
    user = await user_service.get_user_by_email(user_email, session)
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):

        if current_user is None:
            raise UserNotFoundException()

        if not current_user.is_verified:
            raise AccountNotVerifiedException()

        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermissionException()
