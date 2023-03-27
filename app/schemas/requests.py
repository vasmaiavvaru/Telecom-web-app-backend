from pydantic import BaseModel, EmailStr, Field


class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class UserUpdatePasswordRequest(BaseRequest):
    password: str


class UserCreateRequest(BaseRequest):
    email: EmailStr
    password: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    mobile_number: int = Field(alias="mobileNumber")
    chosen_plan_id: int
    postal_address: str = Field(alias="postalAddress")
