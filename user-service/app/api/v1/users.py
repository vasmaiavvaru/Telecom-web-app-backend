import uuid
from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User, UserPlan
from app.schemas.requests import (
    UserCreateRequest,
    UserUpdatePasswordRequest,
    AddPlanRequest,
)
from app.schemas.responses import UserResponse, PlanResponse, UserPlanResponse

# edited
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
from api import deps
# edited

http_client = httpx.AsyncClient()
router = APIRouter()


@router.get("/current", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get current user

    :param current_user: Current user object
    :return: Current user object
    """
    return current_user


@router.delete("/current", status_code=204)
async def delete_current_user(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    """
    Delete current user

    :param current_user: Current user object
    :param session: Async session
    """
    await session.execute(delete(User).where(User.id == current_user.id))
    await session.commit()


@router.post("/reset-password", response_model=UserResponse)
async def reset_current_user_password(
    user_update_password: UserUpdatePasswordRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update current user password

    :param user_update_password: Password update request object
    :param session: Async session
    :param current_user: Current user object
    :return: Updated user object
    """
    current_user.hashed_password = get_password_hash(user_update_password.password)
    session.add(current_user)
    await session.commit()
    return current_user


@router.post("/plan", response_model=UserPlanResponse)
async def plan(
    add_plan_request: AddPlanRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update current user password

    :param add_plan_request: Add plan request object
    :param session: Async session
    :param current_user: Current user object
    :return: Updated user object
    """
    select_prev_plan = await session.execute(
        select(UserPlan).where(
            (UserPlan.user_id == current_user.id) & (UserPlan.active == 1)
        )
    )
    previous_active_plan = select_prev_plan.scalars().first()
    try:
        plan_details = await _get_plan(add_plan_request.plan_id)
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=404, detail="Invalid plan ID.")
    user_plan_id = str(uuid.uuid4())
    new_user_plan = UserPlan(
        id=user_plan_id,
        user_id=current_user.id,
        plan_id=add_plan_request.plan_id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=plan_details.validity),
        active=True,
    )
    if previous_active_plan is not None:
        previous_active_plan.active = False
        session.add(previous_active_plan)
        current_user.active_plan_id = new_user_plan.plan_id
        session.add(current_user)
        session.add(new_user_plan)
    else:
        current_user.active_plan_id = user_plan_id
        session.add(current_user)
        session.add(new_user_plan)
    await session.commit()
    return new_user_plan


async def _get_plan(plan_id: str) -> PlanResponse:
    r = await http_client.get(settings.PLANS_SERVICE_URL + f"/{plan_id}")
    r.raise_for_status()
    return PlanResponse(**r.json())


@router.post("/register", response_model=UserResponse)
async def register_new_user(
    new_user: UserCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
):
    """
    Create new user

    :param new_user: New user request object
    :param session: Async session
    :return: New user object
    """
    result = await session.execute(
        select(User).where(
            (User.mobile_number == new_user.mobile_number)
            | (User.email == new_user.email)
        )
    )
    if result.scalars().first() is not None:
        raise HTTPException(
            status_code=400, detail="Mobile number / Email already exists"
        )
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=new_user.email,
        hashed_password=get_password_hash(new_user.password),
        mobile_number=new_user.mobile_number,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        postal_address=new_user.postal_address,
    )
    session.add(user)
    await session.commit()
    return user


@router.get("/plan", response_model=list[UserPlanResponse])
async def get_current_user_plans(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
):
    """
    Get current user

    :param current_user: Current user object
    :param session: Async session
    :return: Current user object
    """
    results = (
        select(UserPlan)
        .where(UserPlan.user_id == current_user.id)
        .order_by(UserPlan.end_date.desc())
    )
    user_plans = await session.execute(results)
    return user_plans.scalars().all()

# edited
@router.post("/token/decoder", tags=["decoder"])
async def token_decoder(
    session: AsyncSession = Depends(deps.get_session),
    token: str = Depends(deps.reusable_oauth2)
):
    """
    Get current user

    :param current_user: Current user object
    :param session: Async session
    :return: Current user object
   
    """
    payload = jwt.decode(
        token, config.settings.SECRET_KEY, algorithms=[security.JWT_ALGORITHM]
    )
    token_data = security.JWTTokenPayload(**payload)
    result = await session.execute(select(User).where(User.id == token_data.sub))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user 
# edited