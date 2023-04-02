from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class BaseResponse(BaseModel):
    # may define additional fields or config shared across responses
    class Config:
        orm_mode = True


class AccessTokenResponse(BaseResponse):
    token_type: str
    access_token: str
    expires_at: int
    issued_at: int
    refresh_token: str
    refresh_token_expires_at: int
    refresh_token_issued_at: int


class UserResponse(BaseResponse):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    mobile_number: str
    postal_address: str
    active_plan_id: Optional[str]


class UserPlanResponse(BaseResponse):
    start_date: datetime
    end_date: datetime
    active: bool
    plan_id: str

    @validator("start_date", "end_date", pre=True)
    def convert_datetime(cls, v):
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        raise ValueError("Invalid datetime format. Must be ISO 8601 format")


class PlanResponse(BaseResponse):
    id: str
    name: str
    description: str
    price: int
    validity: int
