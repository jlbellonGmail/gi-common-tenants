"""Versioned HTTP and JSON-safe Python facade."""

from __future__ import annotations

from typing import Callable

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from .authorization import TenantContext
from .errors import AuthenticationRequiredError, TenantsError


def _ctx(x_user_id: str | None, x_tenant_id: str | None) -> TenantContext:
    if not x_user_id or not x_tenant_id:
        raise AuthenticationRequiredError()
    return TenantContext(x_user_id, x_tenant_id)


def create_app(service, *, authenticate: Callable[[Request], TenantContext | None] | None = None) -> FastAPI:
    """Create the Common-Tenants API.

    ``authenticate`` is mandatory. Common-Tenants does not parse bearer tokens
    and never treats client-supplied tenant headers as authentication.
    """
    app = FastAPI(title="GI Common Tenants API", version="0.1.1", root_path="")

    @app.exception_handler(TenantsError)
    async def tenants_error(_: Request, exc: TenantsError):
        return JSONResponse(status_code=exc.status, content={"error": exc.public()})

    def context(request: Request, x_user_id: str | None = Header(default=None), x_tenant_id: str | None = Header(default=None)):
        if authenticate is None:
            raise AuthenticationRequiredError()
        result = authenticate(request)
        if result is None:
            raise AuthenticationRequiredError()
        return result

    @app.get("/healthz")
    def healthz(): return {"status": "ok"}

    @app.get("/readyz")
    def readyz(): return {"status": "ready"}

    @app.post("/v1/tenants/{tenant_id}/profile", status_code=201)
    def create_profile(tenant_id: str, payload: dict, ctx: TenantContext = Depends(context)):
        return service.create_profile(ctx, tenant_id=tenant_id, **payload)

    @app.get("/v1/tenants/{tenant_id}/profile")
    def get_profile(tenant_id: str, ctx: TenantContext = Depends(context)): return service.get_profile(ctx, tenant_id)

    @app.patch("/v1/tenants/{tenant_id}/profile")
    def update_profile(tenant_id: str, payload: dict, ctx: TenantContext = Depends(context)):
        return service.update_profile(ctx, tenant_id, int(payload.pop("expected_version")), **payload)

    @app.post("/v1/tenants/{tenant_id}/identifiers", status_code=201)
    def add_identifier(tenant_id: str, payload: dict, ctx: TenantContext = Depends(context)): return service.add_identifier(ctx, tenant_id, **payload)
    @app.get("/v1/tenants/{tenant_id}/identifiers")
    def list_identifiers(tenant_id: str, ctx: TenantContext = Depends(context)): return {"items": service.list_identifiers(ctx, tenant_id)}
    @app.delete("/v1/tenant-identifiers/{identifier_id}")
    def delete_identifier(identifier_id: str, ctx: TenantContext = Depends(context)): return service.delete_identifier(ctx, identifier_id)

    @app.post("/v1/tenants/{tenant_id}/contacts", status_code=201)
    def add_contact(tenant_id: str, payload: dict, ctx: TenantContext = Depends(context)): return service.add_contact(ctx, tenant_id, **payload)
    @app.get("/v1/tenants/{tenant_id}/contacts")
    def list_contacts(tenant_id: str, ctx: TenantContext = Depends(context)): return {"items": service.list_contacts(ctx, tenant_id)}
    @app.post("/v1/tenants/{tenant_id}/addresses", status_code=201)
    def add_address(tenant_id: str, payload: dict, ctx: TenantContext = Depends(context)): return service.add_address(ctx, tenant_id, **payload)
    @app.get("/v1/tenants/{tenant_id}/addresses")
    def list_addresses(tenant_id: str, ctx: TenantContext = Depends(context)): return {"items": service.list_addresses(ctx, tenant_id)}

    @app.get("/v1/plans")
    def list_plans(ctx: TenantContext = Depends(context)): return {"items": service.list_plans(ctx)}
    @app.post("/v1/plans", status_code=201)
    def create_plan(payload: dict, ctx: TenantContext = Depends(context)): return service.save_plan(ctx, **payload)
    @app.post("/v1/plans/{plan_id}/prices", status_code=201)
    def add_price(plan_id: str, payload: dict, ctx: TenantContext = Depends(context)): return service.add_price(ctx, plan_id, **payload)
    @app.post("/v1/plans/{plan_id}/entitlements", status_code=201)
    def add_entitlement(plan_id: str, payload: dict, ctx: TenantContext = Depends(context)): return service.add_entitlement(ctx, plan_id, **payload)

    @app.post("/v1/tenants/{tenant_id}/contracts", status_code=201)
    def create_contract(tenant_id: str, payload: dict, ctx: TenantContext = Depends(context)): return service.create_contract(ctx, tenant_id, **payload)
    @app.get("/v1/tenants/{tenant_id}/contracts")
    def list_contracts(tenant_id: str, ctx: TenantContext = Depends(context)): return {"items": service.list_contracts(ctx, tenant_id)}
    @app.post("/v1/tenants/{tenant_id}/subscriptions", status_code=201)
    def create_subscription(tenant_id: str, payload: dict, ctx: TenantContext = Depends(context)): return service.create_subscription(ctx, tenant_id, **payload)
    @app.get("/v1/tenants/{tenant_id}/subscriptions")
    def list_subscriptions(tenant_id: str, ctx: TenantContext = Depends(context)): return {"items": service.list_subscriptions(ctx, tenant_id)}
    @app.patch("/v1/subscriptions/{subscription_id}")
    def update_subscription(subscription_id: str, payload: dict, ctx: TenantContext = Depends(context)):
        return service.update_subscription(ctx, subscription_id, int(payload.pop("expected_version")), **payload)

    @app.get("/v1/tenants/{tenant_id}/billing")
    def get_billing(tenant_id: str, ctx: TenantContext = Depends(context)): return service.get_billing(ctx, tenant_id)
    @app.put("/v1/tenants/{tenant_id}/billing")
    def save_billing(tenant_id: str, payload: dict, ctx: TenantContext = Depends(context)): return service.save_billing(ctx, tenant_id, **payload)
    return app


class TenantsApi:
    """Framework-independent Python contract over ``TenantService``."""

    def __init__(self, service): self.service = service
    def create_profile(self, context, **payload): return self.service.create_profile(context, **payload)
    def get_profile(self, context, tenant_id): return self.service.get_profile(context, tenant_id)
    def list_identifiers(self, context, tenant_id): return {"items": self.service.list_identifiers(context, tenant_id)}
    def list_contacts(self, context, tenant_id): return {"items": self.service.list_contacts(context, tenant_id)}
    def list_addresses(self, context, tenant_id): return {"items": self.service.list_addresses(context, tenant_id)}
    def list_plans(self, context): return {"items": self.service.list_plans(context)}
    def list_contracts(self, context, tenant_id): return {"items": self.service.list_contracts(context, tenant_id)}
    def list_subscriptions(self, context, tenant_id): return {"items": self.service.list_subscriptions(context, tenant_id)}
    def error(self, exc: Exception): return exc.public() if isinstance(exc, TenantsError) else {"code": "INTERNAL_ERROR", "message": "Tenants operation failed."}
