import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class IAMUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: uuid.UUID
    org_id: uuid.UUID = Field(alias="org_id")
    full_name: str | None = Field(alias="display_name")
    email: str | None
    phone: str | None = None
    avatar_url: str | None = None
    roles: List[str] = []
    is_active: bool = True
    created_at: datetime


class TokenIntrospection(BaseModel):
    model_config = ConfigDict(extra="ignore")

    active: bool
    sub: str
    org_id: uuid.UUID
    client_id: Optional[str] = None
    roles: List[str] = []
    scopes: List[str] = []
    type: str = "access"