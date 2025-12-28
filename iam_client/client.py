import requests
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
        self.timeout = timeout
        self._client_token: Optional[str] = None

    def _get_client_token(self) -> str:
        resp = requests.post(
            f"{self.base_url}/auth/client-token",
            data={
                "tenant_slug": self.tenant_slug,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=self.timeout,
        )

        if resp.status_code != 200:
            raise IAMUnauthorized("Failed to get client token")

        return resp.json()["access_token"]

    def _headers(self):
        if not self._client_token:
            self._client_token = self._get_client_token()
        return {"Authorization": f"Bearer {self._client_token}"}

    def get_user(self, user_id: str) -> IAMUser:
        resp = requests.get(
            f"{self.base_url}/users/{user_id}",
            headers=self._headers(),
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise IAMUnavailable("Failed to fetch user")
        return IAMUser(**resp.json())
