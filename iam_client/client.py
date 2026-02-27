import time
import uuid
import logging
from typing import Optional, Union

import httpx
import jwt
from jwt import PyJWKClient

from .exceptions import (
    IAMError, IAMUnauthorized, IAMAPIError, 
    IAMUnavailable, IAMTokenError
)
from .schemas import IAMUser, TokenIntrospection

logger = logging.getLogger("iam_client")

class IAMClient:
    """Production-grade modular IAM Client (Organization based)."""
    
    def __init__(
        self,
        base_url: str,
        org_slug: str,
        client_id: str,
        client_secret: str,
        timeout: int = 5,
    ):
        self.base_url = base_url.rstrip("/")
        self.org_slug = org_slug
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = httpx.Timeout(timeout)
        
        self._client_token: Optional[str] = None
        self._token_expires_at: float = 0
        
        self.api_client = httpx.AsyncClient(
            base_url=self.base_url, 
            timeout=self.timeout,
            headers={"User-Agent": "IAM-Client-Python/1.1"}
        )
        
        self.jwks_client = PyJWKClient(f"{self.base_url}/.well-known/jwks.json")

    async def _get_client_token(self) -> str:
        """Fetch a fresh service-to-service token."""
        try:
            resp = await self.api_client.post(
                "/auth/client-token",
                json={
                    "org_slug": self.org_slug,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            
            if resp.status_code == 401:
                raise IAMUnauthorized("Invalid client credentials or organization slug")
            
            if resp.status_code != 200:
                raise IAMAPIError(resp.status_code, resp.text)

            data = resp.json()
            token = data["access_token"]
            expires_in = data.get("expires_in", 900)
            
            self._client_token = token
            self._token_expires_at = time.time() + expires_in - 30
            return token
            
        except httpx.RequestError as e:
            raise IAMUnavailable(f"Connection failed: {e}")

    async def _get_auth_headers(self) -> dict:
        if not self._client_token or time.time() > self._token_expires_at:
            await self._get_client_token()
        return {"Authorization": f"Bearer {self._client_token}"}

    async def get_user(self, user_id: Union[str, uuid.UUID]) -> Optional[IAMUser]:
        headers = await self._get_auth_headers()
        
        try:
            resp = await self.api_client.get(
                f"/users/{user_id}",
                headers=headers
            )

            if resp.status_code == 404:
                return None 
            if resp.status_code != 200:
                raise IAMAPIError(resp.status_code, resp.text)

            return IAMUser.model_validate(resp.json())
        except httpx.RequestError as e:
            raise IAMUnavailable(f"Request to IAM failed: {e}")

    def verify_token_locally(self, token: str) -> TokenIntrospection:
        """Verify a JWT locally using JWKS (No network call required)."""
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False}
            )
            
            return TokenIntrospection(
                active=True,
                sub=payload["sub"],
                org_id=uuid.UUID(payload.get("org_id")),
                client_id=payload.get("client_id"),
                roles=payload.get("roles", []),
                scopes=payload.get("scopes", []),
                type=payload.get("type", "access")
            )
        except (jwt.PyJWTError, KeyError, ValueError) as e:
            raise IAMTokenError(f"Token verification failed: {e}")

    async def close(self):
        await self.api_client.aclose()