from typing import Any, Callable
from fastapi import status, FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class BooklyException(Exception):
    """This is the base class for all bookly errors"""


class InvalidTokenException(BooklyException):
    """User has provided an invalid or expired token"""

    # HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail={
    #                 "error": "This token is invalid or expired",
    #                 "resolution": "Please a new token",
    #             },
    #         )


class RevokenTokenException(Exception):
    """User has provided a token that has been revoked"""


class AccessTokenRequiredException(Exception):
    """User has provided a refresh token when an access token is needed"""


class RefreshTokenRequiredException(Exception):
    """User has provided an access token when refresh token is required"""


class UserAlreadyExistsException(Exception):
    """User has provided an email for a user who exists during sign up"""


class InvalidCredentialsException(Exception):
    """User has provided worng password or email during login"""


class InsufficientPermissionException(Exception):
    """User does not have necessary permissions to perform action"""


class AccountNotVerifiedException(Exception):
    """Account not verified kindly verify your account to continue"""


class BookNotFoundException(Exception):
    """Book Not Found"""


class UserNotFoundException(Exception):
    """User Not Found"""


class TagNotFoundException(Exception):
    """Tag Not Found"""


class TagAlreadyExistsException(Exception):
    """Tag already exists"""


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: BooklyException):
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):

    app.add_exception_handler(
        UserAlreadyExistsException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "status": False,
                "message": "User with this email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFoundException,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "status": False,
                "message": "User not found",
                "error_code": "user_not_found",
            },
        ),
    )

    app.add_exception_handler(
        BookNotFoundException,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "status": False,
                "message": "Book not found",
                "error_code": "book_not_found",
            },
        ),
    )

    app.add_exception_handler(
        InvalidCredentialsException,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "status": False,
                "message": "Invalid Email or Password",
                "error_code": "invalid_email",
            },
        ),
    )

    app.add_exception_handler(
        InvalidTokenException,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "status": False,
                "message": "Token is invalid Or Expired",
                "resolution": "Please get a new token",
                "error_code": "invalid_token",
            },
        ),
    )

    app.add_exception_handler(
        RevokenTokenException,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "status": False,
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get a new token",
                "error_code": "token_revoked",
            },
        ),
    )

    app.add_exception_handler(
        AccessTokenRequiredException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "status": False,
                "message": "Please provide a valid access token",
                "resolution": "Please get a new access token",
                "error_code": "access_token_required",
            },
        ),
    )

    app.add_exception_handler(
        AccountNotVerifiedException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "status": False,
                "message": "Account not verified",
                "resolution": "Kindly verify your account to continue",
                "error_code": "account_not_verified",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermissionException,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "status": False,
                "message": "You don not have enough permissions to perform this action",
                "error_code": "insuffient_permissions",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermissionException,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "status": False,
                "message": "You don not have enough permissions to perform this action",
                "error_code": "insuffient_permissions",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exception):
        return JSONResponse(
            content={
                "message": "Ooops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
