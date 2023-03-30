from pydantic import BaseModel


class BaseResponse(BaseModel):
    # may define additional fields or config shared across responses
    class Config:
        orm_mode = True


class PlanResponse(BaseResponse):
    id: str
    name: str
    description: str
    price: int
    validity: int
