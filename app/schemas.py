from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


# ===== User Schemas =====
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    my_role: str
    member_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectMemberResponse(BaseModel):
    user_id: UUID
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True

class ProjectDetailResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_by: UUID
    created_at: datetime
    members: list[ProjectMemberResponse]

    class Config:
        from_attributes = True

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None

class MemberAdd(BaseModel):
    email: EmailStr
    role: Optional[str] = Field("member", pattern="^(admin|member)$")

class MemberRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(admin|member)$")