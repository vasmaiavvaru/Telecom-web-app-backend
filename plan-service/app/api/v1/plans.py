from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models import Plans
from app.schemas.responses import PlanResponse

router = APIRouter()


@router.get("/{plan_id}", response_model=PlanResponse)
async def read_current_user(
    plan_id: str,
    session: AsyncSession = Depends(deps.get_session),
):
    """
    Get single plan by ID

    :param plan_id: Plan ID
    :param session: Async session
    :return: Requested plan object
    """
    result = await session.execute(select(Plans).where(Plans.id == plan_id))
    plan = result.scalars().first()
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.get("/", response_model=list[PlanResponse])
async def read_current_user(
    session: AsyncSession = Depends(deps.get_session),
):
    """
    Get all plans

    :param session: Async session
    :return: Requested plan object
    """
    result = await session.execute(select(Plans))
    return result.scalars().all()
