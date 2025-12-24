from pydantic import BaseModel
from typing import List
import uuid


class IAMUser(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str | None
    phone: str | None
    roles: List[str]
    is_active: bool


class TokenIntrospection(BaseModel):
    active: bool
    sub: uuid.UUID
    tenant_id: uuid.UUID
    client_id: uuid.UUID
    roles: List[str]
    scopes: List[str]
