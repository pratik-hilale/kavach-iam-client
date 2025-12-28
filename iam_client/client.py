import httpx
from typing import Optional
from .schemas import IAMUser, TokenIntrospection
from .exceptions import IAMUnauthorized, IAMUnavailable

class IAMClient:
    def __init__(
        self,
        base_url: str,
        tenant_slug: str,
        client_id: str,
        client_secret: str,
        timeout: int = 5,
    ):
        self.base_url = base_url.rstrip("/")
        self.tenant_slug = tenant_slug
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = httpx.Timeout(timeout)
        self._client_token: Optional[str] = None
        # Use a persistent client for connection pooling
        self.api_client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def _get_client_token(self) -> str:
        """Asynchronously fetch the service-to-service token."""
        resp = await self.api_client.post(
            "/auth/client-token",
            json={
                "tenant_slug": self.tenant_slug,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )

        if resp.status_code != 200:
            raise IAMUnauthorized("Failed to get client token")

        return resp.json()["access_token"]

    async def _get_auth_headers(self):
        """Ensure token exists and return headers."""
        if not self._client_token:
            self._client_token = await self._get_client_token()
        return {"Authorization": f"Bearer {self._client_token}"}

    async def get_user(self, user_id: str) -> IAMUser:
        """The standard approach for fetching a user by UUID."""
        headers = await self._get_auth_headers()
        
        # Note: We use the standardized path /{user_id} here
        resp = await self.api_client.get(
            f"/users/{user_id}",
            headers=headers
        )

        if resp.status_code == 404:
            # Handle 404 gracefully or raise a specific exception
            return None 
        if resp.status_code != 200:
            raise IAMUnavailable(f"IAM API returned {resp.status_code}")

        return IAMUser(**resp.json())

    async def close(self):
        """Clean up the underlying connection pool."""
        await self.api_client.aclose()