import time
from collections.abc import AsyncGenerator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import config, security
from app.core.session import async_session
from app.models import User

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="auth/access-token")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a new session for each request.

    :return: AsyncSession
    """
    async with async_session() as session:
        yield session


async def get_current_user(
    session: AsyncSession = Depends(get_session), token: str = Depends(reusable_oauth2)
) -> User:
    """
    Get the current user from the token.

    :param session: User session
    :param token: JWT token
    :return: User
    :raises HTTPException: If the token is invalid
    """
    try:
        payload = jwt.decode(
            token, config.settings.SECRET_KEY, algorithms=[security.JWT_ALGORITHM]
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )
    # JWT guarantees payload will be unchanged (and thus valid), no errors here
    token_data = security.JWTTokenPayload(**payload)

    if token_data.refresh:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials, cannot use refresh token",
        )
    now = int(time.time())
    if now < token_data.issued_at or now > token_data.expires_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials, token expired or not yet valid",
        )

    result = await session.execute(select(User).where(User.id == token_data.sub))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user
