"""Adapters for the published GI-PLATFORM-CORE v0.3.0 contracts.

The Python adapter accepts the real ``CoreApi`` object. The HTTP adapter only
implements operations published by Core's checked-in HTTP contract and fails
closed for capabilities that Core has not published over HTTP.
"""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .errors import CapabilityUnavailableError, CoreUnavailableError, ForbiddenError, NotFoundError, UnsupportedCoreContractError


class CoreApiAdapter:
    contract_version = "0.3.0"

    def __init__(self, api):
        self.api = api

    def create_tenant(self, name: str) -> dict:
        result = self.api.create_tenant(name)
        if not isinstance(result, dict) or result.get("contract_version") != self.contract_version:
            raise UnsupportedCoreContractError()
        tenant_id = result.get("tenant_id") or result.get("id")
        if not tenant_id:
            raise UnsupportedCoreContractError()
        result["tenant_id"] = tenant_id
        return result

    def list_tenants(self, user_id: str) -> list[dict]:
        result = self.api.list_tenants(user_id)
        if not isinstance(result, list):
            raise UnsupportedCoreContractError()
        return result

    def tenant_exists(self, tenant_id: str) -> bool:
        # Core's published Python contract has no direct get_tenant operation.
        # Listing is the public read boundary and remains authorization-aware.
        return any(item.get("tenant_id", item.get("id")) == tenant_id for item in self.list_tenants("service"))

    def authorize(self, user_id: str, tenant_id: str, permission: str, location_id: str | None = None) -> dict:
        result = self.api.authorize(user_id, tenant_id, permission, location_id)
        if not isinstance(result, dict):
            raise UnsupportedCoreContractError()
        return result


class HttpCoreAdapter:
    """Small HTTP client for Core's published v0.3 tenant HTTP surface.

    Core v0.3.0 publishes tenant identity operations over HTTP while tenant
    creation, listing and authorization remain Python-only contracts.
    """

    def __init__(self, base_url: str, bearer_token: str, *, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.bearer_token = bearer_token
        self.timeout = timeout

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        body = None if payload is None else json.dumps(payload).encode()
        request = Request(self.base_url + path, data=body, method=method, headers={
            "Accept": "application/json", "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bearer_token}",
        })
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read() or b"{}")
        except HTTPError as exc:
            if exc.code in {401, 403}:
                raise ForbiddenError() from exc
            if exc.code == 404:
                raise NotFoundError() from exc
            raise CoreUnavailableError() from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise CoreUnavailableError() from exc

    def validate_identity(self, tenant_id: str, user_id: str, external_subject: str) -> dict:
        return self._request("POST", f"/v1/tenants/{tenant_id}/identity-validation", {
            "user_id": user_id, "external_subject": external_subject,
        })

    def link_identity(self, tenant_id: str, person_id: str, user_id: str, external_subject: str) -> dict:
        return self._request("POST", f"/v1/tenants/{tenant_id}/identity-links", {
            "person_id": person_id, "user_id": user_id, "external_subject": external_subject,
        })

    def unlink_identity(self, tenant_id: str, person_id: str) -> dict:
        return self._request("DELETE", f"/v1/tenants/{tenant_id}/identity-links/{person_id}")

    def authorize(self, user_id: str, tenant_id: str, permission: str, location_id: str | None = None) -> dict:
        raise CapabilityUnavailableError("Core v0.3.0 does not publish authorization over its checked-in HTTP contract")

    def create_tenant(self, name: str) -> dict:
        raise CapabilityUnavailableError("Core v0.3.0 does not publish tenant creation over its checked-in HTTP contract")

    def list_tenants(self, user_id: str) -> list[dict]:
        raise CapabilityUnavailableError("Core v0.3.0 does not publish tenant listing over its checked-in HTTP contract")
