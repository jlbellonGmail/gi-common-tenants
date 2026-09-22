"""Tenant context and fail-closed authorization boundary."""

from dataclasses import dataclass

from .errors import ForbiddenError, CoreUnavailableError, UnsupportedCoreContractError


@dataclass(frozen=True)
class TenantContext:
    user_id: str
    tenant_id: str
    location_id: str | None = None


class Authorizer:
    def __init__(self, core):
        self.core = core

    def require(self, context: TenantContext, permission: str) -> None:
        try:
            response = self.core.authorize(context.user_id, context.tenant_id, permission, context.location_id)
        except (ForbiddenError, UnsupportedCoreContractError):
            raise
        except Exception as exc:
            raise CoreUnavailableError() from exc
        if not isinstance(response, dict) or response.get("contract_version") not in {"0.1.0", "0.3.0"}:
            raise UnsupportedCoreContractError()
        if response.get("allowed") is not True:
            raise ForbiddenError()
        returned = response.get("context") or {}
        if returned.get("user_id") != context.user_id or returned.get("tenant_id", returned.get("organization_id")) != context.tenant_id:
            raise ForbiddenError()
