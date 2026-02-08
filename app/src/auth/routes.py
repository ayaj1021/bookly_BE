from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from auth.schema import (
    UserCreate,
    PasswordResetConfirm,
    UserLogin,
    UserBooksModel,
    EmailModel,
    PasswordResetRequest,
)
from auth.service import UserService
from db.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from utils import Tokens, Hash, create_url_safe_token, decode_url_safe_token
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from auth.dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)

from mail import mail, create_message

from errors import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    InvalidTokenException,
    UserNotFoundException,
)
from db.redis import add_jti_to_blocklist
from config import Config
from fastapi.encoders import jsonable_encoder
from celery_tasks import send_email


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses
    print(emails)

    html = "<h1>Welcome to Bookly</h1>"

    subject = "Welcome to our app"

    # message = create_message(recipients=emails, subject="Welcome", body=html)

    # await mail.send_message(message)

    # This is we using celery tasks
    send_email.delay(emails, subject, html)

    return {"message": "Email sent successfully"}


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    bg_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise UserAlreadyExistsException()

    token = create_url_safe_token({"email": email})

    new_user = await user_service.create_user(user_data, session)
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    html_message = f"""
    <h1> Verify your Email</h1>

    <p> Please click this <a href="{link}">link</a> to verify your email </p>



    """

    emails = [email]
    subject = "Verify Your Email"

    # This is we using celery tasks
    send_email.delay(emails, subject, html_message)

    # message = create_message(
    #     recipients=[email], subject="Verify your email", body=html_message
    # )

    # #We can still use fast API background tasks

    # bg_tasks.add_task(mail.send_message, message)

    return JSONResponse(
        content={
            "status": True,
            "message": "Account Created! Kindly check your email to verify your account",
            "user": jsonable_encoder(new_user),
        }
    )


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFoundException()

        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={
                "status": True,
                "message": "Account verified successfully",
            },
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"status": False, "message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.post("/login")
async def login(login_data: UserLogin, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = Hash.verify_password(password, user.password_hash)

        if password_valid:
            access_token = Tokens.create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                }
            )

            refresh_token = Tokens.create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "status": str(status.HTTP_200_OK),
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "user": {
                        "uid": str(user.uid),
                        "email": user.email,
                        "user_name": user.username,
                        "is_verified": user.is_verified,
                    },
                }
            )

    raise InvalidCredentialsException()


@auth_router.get("/refresh_token")
async def get_new_access_token(token_detials: dict = Depends(RefreshTokenBearer())):
    expiry_time_stamp = token_detials["exp"]

    if datetime.fromtimestamp(expiry_time_stamp) > datetime.now():
        new_access_token = Tokens.create_access_token(user_data=token_detials["user"])

        return JSONResponse(
            content={
                "success": True,
                "message": "Access token generated successfully",
                "access_token": new_access_token,
            }
        )
    raise InvalidTokenException()


@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message": "Logged out successfully",
        },
        status_code=status.HTTP_200_OK,
    )


"""
Steps to run password reset
1. PROVIDE THE EMAIL -> password reset request
2. SEND PASSWORD RESET LINK
3. RESET PASSWORD -> password reset confirmation

"""


@auth_router.post("/password_reset_request")
async def password_reset_request(email_data: PasswordResetRequest):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    html_message = f"""
    <h1> Reset Your Password</h1>

    <p> Please click this <a href="{link}">link</a> to Reset Your Password </p>

    """

    message = create_message(
        recipients=[email], subject="Reset Your Password", body=html_message
    )

    await mail.send_message(message)
    return JSONResponse(
        content={
            "status": True,
            "message": "Please check your email for your password reset link",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirm,
    session: AsyncSession = Depends(get_session),
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passowrds do not match"
        )
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFoundException()

        password_hash = Hash.generate_password_hash(new_password)

        await user_service.update_user(user, {"password_hash": password_hash}, session)

        return JSONResponse(
            content={
                "status": True,
                "message": "Password reset successfully",
            },
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"status": False, "message": "Error Resetting password"},
        status_code=status.HTTP_400_BAD_REQUEST,
    )
