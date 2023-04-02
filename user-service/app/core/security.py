"""Black-box security shortcuts to generate JWT tokens and password hashing and verifcation."""
import time
from typing import Union

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core import config
from app.schemas.responses import AccessTokenResponse
from sqlalchemy.orm import Session


# Typing
StrOrInt = Union[str, int]
StrOrIntOrBool = Union[StrOrInt, bool]

# Constants
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECS = config.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
REFRESH_TOKEN_EXPIRE_SECS = config.settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
PWD_CONTEXT = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=config.settings.SECURITY_BCRYPT_ROUNDS,
)


class JWTTokenPayload(BaseModel):
    """ Stores the JWT token payload after decoding. """
    sub: StrOrInt
    refresh: bool
    issued_at: int
    expires_at: int


def create_jwt_token(subject: StrOrInt, exp_secs: int, refresh: bool) -> tuple[str, int, int]:
    """
    Create a JWT token with the given subject, expiration time, and refresh flag.

    :param subject: anything unique to user, id or email etc.
    :param exp_secs: expire time in seconds
    :param refresh: if True, this is refresh token
    :return: tuple of (encoded_jwt, expires_at, issued_at)
    """

    issued_at = int(time.time())
    expires_at = issued_at + exp_secs

    to_encode: dict[str, StrOrIntOrBool] = {
        "issued_at": issued_at,
        "expires_at": expires_at,
        "sub": subject,
        "refresh": refresh,
    }
    encoded_jwt = jwt.encode(
        to_encode,
        key=config.settings.SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    return encoded_jwt, expires_at, issued_at


def generate_access_token_response(subject: StrOrInt) -> AccessTokenResponse:
    """
    Generate access token and refresh token response.

    :param subject: anything unique to user, id or email etc.
    :return: AccessTokenResponse
    """
    access_token, expires_at, issued_at = create_jwt_token(
        subject, ACCESS_TOKEN_EXPIRE_SECS, refresh=False
    )
    refresh_token, refresh_expires_at, refresh_issued_at = create_jwt_token(
        subject, REFRESH_TOKEN_EXPIRE_SECS, refresh=True
    )
    return AccessTokenResponse(
        token_type="Bearer",
        access_token=access_token,
        expires_at=expires_at,
        issued_at=issued_at,
        refresh_token=refresh_token,
        refresh_token_expires_at=refresh_expires_at,
        refresh_token_issued_at=refresh_issued_at,
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password match with hashed password.
    Applies passlib context based on bcrypt algorithm on plain password.
    It takes about 0.3s for default 12 rounds of SECURITY_BCRYPT_DEFAULT_ROUNDS.

    :param plain_password: Plain password
    :param hashed_password: Hashed password
    :return: True if password matches, False otherwise
    """
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash password with passlib context based on bcrypt algorithm.

    :param password: Plain password
    :return: Hashed password
    """
    return PWD_CONTEXT.hash(password)

