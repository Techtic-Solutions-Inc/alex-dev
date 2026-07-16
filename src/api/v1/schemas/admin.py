import uuid

from pydantic import BaseModel, Field

from src.api.v1.models.enums import AccountStatus


class AdminUpdateUserRequest(BaseModel):
    user_id: uuid.UUID
    status: AccountStatus = Field(description='New account status: active, inactive, or suspended')


class AdminUpdateUserResponse(BaseModel):
    message: str = 'User account updated successfully'
