"""Application services and commercial invariants for Common-Tenants."""

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import uuid4

from .authorization import Authorizer, TenantContext
from .errors import CapabilityUnavailableError, ConflictError, IsolationError, NotFoundError, ValidationError


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def required(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} is required")
    return value.strip()


def enum(value: Any, field: str, choices: set[str]) -> str:
    value = required(value, field).lower()
    if value not in choices:
        raise ValidationError(f"{field} must be one of {sorted(choices)}")
    return value


def money(value: Any) -> str:
    try:
        result = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValidationError("amount must be a decimal") from exc
    if result < 0:
        raise ValidationError("amount must not be negative")
    return format(result, "f")


class TenantService:
    """Use cases over a repository and a published Core authorization port."""

    def __init__(self, repository, core, *, bootstrap_authorizer=None):
        self.repository = repository
        self.core = core
        self.auth = Authorizer(core)
        self.bootstrap_authorizer = bootstrap_authorizer

    def _scope(self, ctx: TenantContext, tenant_id: str, permission: str) -> None:
        if ctx.tenant_id != str(tenant_id):
            raise IsolationError()
        self.auth.require(ctx, permission)
        if hasattr(self.repository, "set_context"):
            self.repository.set_context(ctx.tenant_id, ctx.user_id)

    def _audit(self, ctx: TenantContext | None, tenant_id: str | None, action: str, resource: str, resource_id: str, outcome="success"):
        self.repository.record_audit({
            "event_id": self.repository.new_id(), "tenant_id": tenant_id, "actor_user_id": ctx.user_id if ctx else None,
            "action": action, "resource": resource, "resource_id": resource_id, "outcome": outcome, "occurred_at": utcnow(),
        })

    def _tenant_exists(self, tenant_id: str, user_id: str) -> None:
        # The service deliberately delegates identity existence to Core. A
        # profile may be created only after Core accepts the tenant context.
        if not tenant_id:
            raise ValidationError("tenant_id is required")
        list_tenants = getattr(self.core, "list_tenants", None)
        if not callable(list_tenants):
            raise CapabilityUnavailableError("Core tenant listing is required to validate tenant identity")
        tenants = list_tenants(user_id)
        if not any(str(item.get("tenant_id") or item.get("id")) == str(tenant_id) for item in tenants if isinstance(item, dict)):
            raise NotFoundError("tenant not found in Core authorization context")

    def _subscription_history(self, before, after, event_type):
        if not hasattr(self.repository, "record_subscription_history"):
            return
        self.repository.record_subscription_history({
            "history_id": self.repository.new_id(), "subscription_id": after["subscription_id"],
            "tenant_id": after["tenant_id"], "event_type": event_type,
            "previous_state": before, "new_state": after, "occurred_at": utcnow(),
        })

    def _global_scope(self, ctx: TenantContext, permission: str) -> None:
        self.auth.require(ctx, permission)
        if hasattr(self.repository, "set_context"):
            self.repository.set_context(ctx.tenant_id, ctx.user_id)

    def create_tenant(self, ctx: TenantContext, *, display_name: str, legal_name: str, entity_type: str, country_code: str, locale="es-AR", timezone_name="UTC", tenant_name: str | None = None):
        """Create Core's technical root, then persist the administrative profile."""
        if self.bootstrap_authorizer is None or not self.bootstrap_authorizer(ctx):
            raise CapabilityUnavailableError("tenant creation requires a host-controlled Core bootstrap authorization")
        name = tenant_name or legal_name or display_name
        core_tenant = self.core.create_tenant(required(name, "tenant_name"))
        tenant_id = str(core_tenant.get("tenant_id") or core_tenant.get("id"))
        if not tenant_id:
            raise ValidationError("Core did not return tenant_id")
        if ctx.tenant_id != tenant_id:
            raise IsolationError()
        return self._create_profile(ctx, tenant_id=tenant_id, display_name=display_name, legal_name=legal_name, entity_type=entity_type, country_code=country_code, locale=locale, timezone=timezone_name, validate_core=False)

    def create_profile(self, ctx: TenantContext, *, tenant_id: str, display_name: str, legal_name: str, entity_type: str, country_code: str, locale="es-AR", timezone="UTC"):
        return self._create_profile(ctx, tenant_id=tenant_id, display_name=display_name, legal_name=legal_name, entity_type=entity_type, country_code=country_code, locale=locale, timezone=timezone, validate_core=True)

    def _create_profile(self, ctx: TenantContext, *, tenant_id: str, display_name: str, legal_name: str, entity_type: str, country_code: str, locale="es-AR", timezone="UTC", validate_core=True):
        self._scope(ctx, tenant_id, "tenants:profile:write")
        if validate_core:
            self._tenant_exists(tenant_id, ctx.user_id)
        row = {"tenant_id": str(tenant_id), "display_name": required(display_name, "display_name"), "legal_name": required(legal_name, "legal_name"), "entity_type": enum(entity_type, "entity_type", {"individual", "legal_entity"}), "country_code": required(country_code, "country_code").upper(), "locale": required(locale, "locale"), "timezone": required(timezone, "timezone"), "version": 1, "created_at": utcnow(), "updated_at": utcnow()}
        with self.repository.transaction():
            if self.repository.get("tenant_profiles", tenant_id): raise ConflictError()
            self.repository.put("tenant_profiles", tenant_id, row); self._audit(ctx, tenant_id, "profile.created", "tenant_profile", tenant_id)
        return row

    def get_profile(self, ctx: TenantContext, tenant_id: str):
        self._scope(ctx, tenant_id, "tenants:profile:read")
        return self.repository.require("tenant_profiles", tenant_id)

    def update_profile(self, ctx: TenantContext, tenant_id: str, expected_version: int, **changes):
        self._scope(ctx, tenant_id, "tenants:profile:write")
        row = self.repository.require("tenant_profiles", tenant_id)
        allowed = {"display_name", "legal_name", "entity_type", "country_code", "locale", "timezone"}
        unknown = set(changes) - allowed
        if unknown: raise ValidationError(f"unknown profile fields: {sorted(unknown)}")
        row.update(changes); row["updated_at"] = utcnow()
        if "entity_type" in changes: row["entity_type"] = enum(changes["entity_type"], "entity_type", {"individual", "legal_entity"})
        if "country_code" in changes: row["country_code"] = required(changes["country_code"], "country_code").upper()
        with self.repository.transaction():
            result = self.repository.put("tenant_profiles", tenant_id, row, expected_version=expected_version); self._audit(ctx, tenant_id, "profile.updated", "tenant_profile", tenant_id); return result

    def _tenant_child(self, ctx, table, key_field, key, permission):
        row = self.repository.require(table, key)
        self._scope(ctx, row["tenant_id"], permission)
        return row

    def add_identifier(self, ctx: TenantContext, tenant_id: str, *, country_code: str, identifier_type: str, identifier_value: str, is_primary=False):
        self._scope(ctx, tenant_id, "tenants:identifier:write"); value = required(identifier_value, "identifier_value"); normalized = "".join(ch for ch in value.upper() if ch.isalnum())
        if not normalized: raise ValidationError("identifier_value is invalid")
        row = {"identifier_id": self.repository.new_id(), "tenant_id": str(tenant_id), "country_code": required(country_code, "country_code").upper(), "identifier_type": required(identifier_type, "identifier_type").lower(), "identifier_value": value, "normalized_value": normalized, "is_primary": bool(is_primary), "created_at": utcnow()}
        with self.repository.transaction():
            self.repository.unique("tenant_identifiers", ("tenant_id", "country_code", "identifier_type", "normalized_value"), row)
            if is_primary:
                for old in self.repository.list("tenant_identifiers", tenant_id=tenant_id): old["is_primary"] = False; self.repository.put("tenant_identifiers", old["identifier_id"], old)
            self.repository.put("tenant_identifiers", row["identifier_id"], row); self._audit(ctx, tenant_id, "identifier.created", "tenant_identifier", row["identifier_id"])
        return row

    def list_identifiers(self, ctx, tenant_id): self._scope(ctx, tenant_id, "tenants:identifier:read"); return self.repository.list("tenant_identifiers", tenant_id=tenant_id)
    def delete_identifier(self, ctx, identifier_id):
        row = self._tenant_child(ctx, "tenant_identifiers", "identifier_id", identifier_id, "tenants:identifier:write"); self.repository.delete("tenant_identifiers", identifier_id); self._audit(ctx, row["tenant_id"], "identifier.deleted", "tenant_identifier", identifier_id); return {"deleted": True}

    def add_contact(self, ctx, tenant_id, **data): return self._add_child(ctx, "tenant_contacts", "contact_id", tenant_id, "tenants:contact:write", {"contact_name", "contact_role", "email", "phone", "is_primary"}, data)
    def list_contacts(self, ctx, tenant_id): self._scope(ctx, tenant_id, "tenants:contact:read"); return self.repository.list("tenant_contacts", tenant_id=tenant_id)
    def add_address(self, ctx, tenant_id, **data): return self._add_child(ctx, "tenant_addresses", "address_id", tenant_id, "tenants:address:write", {"address_type", "address_line1", "address_line2", "city", "region", "postal_code", "country_code", "is_primary"}, data)
    def list_addresses(self, ctx, tenant_id): self._scope(ctx, tenant_id, "tenants:address:read"); return self.repository.list("tenant_addresses", tenant_id=tenant_id)

    def _add_child(self, ctx, table, id_field, tenant_id, permission, allowed, data):
        self._scope(ctx, tenant_id, permission); unknown = set(data) - allowed
        if unknown: raise ValidationError(f"unknown fields: {sorted(unknown)}")
        row = {id_field: self.repository.new_id(), "tenant_id": str(tenant_id), **data, "created_at": utcnow(), "updated_at": utcnow()}
        for field in allowed - {"address_line2", "is_primary", "phone", "email"}:
            if field in row: row[field] = required(row[field], field)
        if table == "tenant_contacts" and row.get("email"): row["email"] = row["email"].strip().lower()
        if table == "tenant_addresses": row["country_code"] = required(row.get("country_code"), "country_code").upper()
        with self.repository.transaction():
            if row.get("is_primary"):
                for old in self.repository.list(table, tenant_id=tenant_id): old["is_primary"] = False; self.repository.put(table, old[id_field], old)
            self.repository.put(table, row[id_field], row); self._audit(ctx, tenant_id, f"{table}.created", table, row[id_field])
        return row

    def save_plan(self, ctx, **data):
        self._global_scope(ctx, "tenants:catalog:write"); row = {"plan_id": self.repository.new_id(), "code": required(data.get("code"), "code"), "name": required(data.get("name"), "name"), "description": data.get("description"), "is_active": data.get("is_active", True), "created_at": utcnow(), "updated_at": utcnow()}
        with self.repository.transaction(): self.repository.unique("service_plans", ("code",), row); self.repository.put("service_plans", row["plan_id"], row); self._audit(ctx, None, "plan.created", "service_plan", row["plan_id"])
        return row
    def list_plans(self, ctx): self._global_scope(ctx, "tenants:catalog:read"); return self.repository.list("service_plans")
    def update_plan(self, ctx, plan_id, **changes):
        self._global_scope(ctx, "tenants:catalog:write"); row=self.repository.require("service_plans", plan_id)
        if set(changes) - {"name", "description", "is_active"}: raise ValidationError("unknown plan fields")
        row.update(changes); row["updated_at"] = utcnow()
        with self.repository.transaction(): self.repository.put("service_plans", plan_id, row); self._audit(ctx, None, "plan.updated", "service_plan", plan_id); return row
    def deactivate_plan(self, ctx, plan_id): return self.update_plan(ctx, plan_id, is_active=False)
    def add_price(self, ctx, plan_id, **data):
        self._global_scope(ctx, "tenants:catalog:write"); self.repository.require("service_plans", plan_id); row = {"price_id": self.repository.new_id(), "plan_id": plan_id, "currency_code": required(data.get("currency_code"), "currency_code").upper(), "amount": money(data.get("amount")), "billing_interval": enum(data.get("billing_interval"), "billing_interval", {"day", "week", "month", "year"}), "billing_interval_count": int(data.get("billing_interval_count", 1)), "effective_from": required(data.get("effective_from"), "effective_from"), "effective_until": data.get("effective_until"), "is_active": data.get("is_active", True), "created_at": utcnow(), "updated_at": utcnow()}
        if row["billing_interval_count"] < 1: raise ValidationError("billing_interval_count must be positive")
        with self.repository.transaction(): self.repository.put("service_plan_prices", row["price_id"], row); self._audit(ctx, None, "plan_price.created", "service_plan_price", row["price_id"])
        return row
    def add_entitlement(self, ctx, plan_id, **data):
        self._global_scope(ctx, "tenants:catalog:write"); self.repository.require("service_plans", plan_id); typ = enum(data.get("entitlement_type"), "entitlement_type", {"module", "feature", "limit", "quantity"}); value = data.get("entitlement_value")
        if not isinstance(value, (str, int, float, bool, dict, list)): raise ValidationError("entitlement_value must be JSON scalar or object")
        row = {"entitlement_id": self.repository.new_id(), "plan_id": plan_id, "entitlement_code": required(data.get("entitlement_code"), "entitlement_code"), "entitlement_type": typ, "entitlement_value": value, "effective_from": required(data.get("effective_from"), "effective_from"), "effective_until": data.get("effective_until"), "created_at": utcnow(), "updated_at": utcnow()}
        with self.repository.transaction(): self.repository.unique("service_plan_entitlements", ("plan_id", "entitlement_code", "effective_from"), row); self.repository.put("service_plan_entitlements", row["entitlement_id"], row); self._audit(ctx, None, "plan_entitlement.created", "service_plan_entitlement", row["entitlement_id"])
        return row

    def create_contract(self, ctx, tenant_id, **data):
        self._scope(ctx, tenant_id, "tenants:contract:write"); start = required(data.get("effective_from"), "effective_from"); end = data.get("effective_until");
        if end and end < start: raise ValidationError("contract period is invalid")
        row = {"contract_id": self.repository.new_id(), "tenant_id": tenant_id, "contract_number": required(data.get("contract_number"), "contract_number"), "status": enum(data.get("status", "draft"), "status", {"draft", "pending", "active", "expired", "terminated", "renewed"}), "signed_at": data.get("signed_at"), "effective_from": start, "effective_until": end, "document_reference": data.get("document_reference"), "created_at": utcnow()}
        with self.repository.transaction(): self.repository.unique("tenant_contracts", ("contract_number",), row); self.repository.put("tenant_contracts", row["contract_id"], row); self._audit(ctx, tenant_id, "contract.created", "tenant_contract", row["contract_id"])
        return row
    def list_contracts(self, ctx, tenant_id): self._scope(ctx, tenant_id, "tenants:contract:read"); return self.repository.list("tenant_contracts", tenant_id=tenant_id)

    def create_subscription(self, ctx, tenant_id, **data):
        self._scope(ctx, tenant_id, "tenants:subscription:write"); contract = self.repository.require("tenant_contracts", data.get("contract_id")); price = self.repository.require("service_plan_prices", data.get("price_id")); plan_id = str(data.get("plan_id"))
        if contract["tenant_id"] != tenant_id or price["plan_id"] != plan_id: raise IsolationError()
        row = {"subscription_id": self.repository.new_id(), "tenant_id": tenant_id, "contract_id": contract["contract_id"], "plan_id": plan_id, "price_id": price["price_id"], "status": enum(data.get("status", "pending"), "status", {"pending", "active", "canceled", "expired", "past_due"}), "started_at": required(data.get("started_at"), "started_at"), "current_period_start": required(data.get("current_period_start"), "current_period_start"), "current_period_end": required(data.get("current_period_end"), "current_period_end"), "cancel_at": data.get("cancel_at"), "canceled_at": data.get("canceled_at"), "created_at": utcnow(), "updated_at": utcnow(), "version": 1, "price_snapshot": {"amount": price["amount"], "currency_code": price["currency_code"], "billing_interval": price["billing_interval"], "billing_interval_count": price["billing_interval_count"]}}
        if row["current_period_end"] <= row["current_period_start"]: raise ValidationError("subscription period is invalid")
        with self.repository.transaction():
            active = self.repository.list("tenant_subscriptions", tenant_id=tenant_id, filters={"status": "active"})
            if any(s["plan_id"] == plan_id for s in active): raise ConflictError()
            self.repository.put("tenant_subscriptions", row["subscription_id"], row); self._audit(ctx, tenant_id, "subscription.created", "tenant_subscription", row["subscription_id"])
            self._subscription_history(None, row, "created")
        return row
    def list_subscriptions(self, ctx, tenant_id): self._scope(ctx, tenant_id, "tenants:subscription:read"); return self.repository.list("tenant_subscriptions", tenant_id=tenant_id)
    def update_subscription(self, ctx, subscription_id, expected_version, **changes):
        row = self._tenant_child(ctx, "tenant_subscriptions", "subscription_id", subscription_id, "tenants:subscription:write"); allowed = {"status", "cancel_at", "canceled_at", "current_period_start", "current_period_end"}; unknown = set(changes)-allowed
        if unknown: raise ValidationError(f"unknown subscription fields: {sorted(unknown)}")
        if "status" in changes: changes["status"] = enum(changes["status"], "status", {"pending", "active", "canceled", "expired", "past_due"})
        before = dict(row)
        row.update(changes); row["updated_at"] = utcnow()
        with self.repository.transaction():
            result=self.repository.put("tenant_subscriptions", subscription_id, row, expected_version=expected_version); self._audit(ctx, row["tenant_id"], "subscription.updated", "tenant_subscription", subscription_id); self._subscription_history(before, result, "updated"); return result

    def renew_subscription(self, ctx, subscription_id, *, current_period_start, current_period_end):
        row = self._tenant_child(ctx, "tenant_subscriptions", "subscription_id", subscription_id, "tenants:subscription:write")
        if current_period_end <= current_period_start or current_period_start < row["current_period_end"]:
            raise ValidationError("renewal period is invalid")
        return self.update_subscription(ctx, subscription_id, row["version"], current_period_start=current_period_start, current_period_end=current_period_end, status="active")

    def cancel_subscription(self, ctx, subscription_id, *, cancel_at=None, immediate=False):
        row = self._tenant_child(ctx, "tenant_subscriptions", "subscription_id", subscription_id, "tenants:subscription:write")
        when = cancel_at or row["current_period_end"]
        return self.update_subscription(ctx, subscription_id, row["version"], cancel_at=when, canceled_at=utcnow() if immediate else None, status="canceled" if immediate else row["status"])

    def change_subscription_plan(self, ctx, subscription_id, *, price_id, current_period_start, current_period_end):
        row = self._tenant_child(ctx, "tenant_subscriptions", "subscription_id", subscription_id, "tenants:subscription:write")
        price = self.repository.require("service_plan_prices", price_id)
        if price["plan_id"] == row["plan_id"] or current_period_end <= current_period_start:
            raise ValidationError("a plan change requires a different plan and valid period")
        before = dict(row)
        row.update({"plan_id": price["plan_id"], "price_id": price_id, "current_period_start": current_period_start, "current_period_end": current_period_end, "price_snapshot": {"amount": price["amount"], "currency_code": price["currency_code"], "billing_interval": price["billing_interval"], "billing_interval_count": price["billing_interval_count"]}, "updated_at": utcnow()})
        with self.repository.transaction():
            result=self.repository.put("tenant_subscriptions", subscription_id, row, expected_version=row["version"]); self._audit(ctx, row["tenant_id"], "subscription.plan_changed", "tenant_subscription", subscription_id); self._subscription_history(before, result, "plan_changed"); return result

    def update_contract(self, ctx, contract_id, **changes):
        row = self._tenant_child(ctx, "tenant_contracts", "contract_id", contract_id, "tenants:contract:write")
        allowed = {"status", "effective_until", "document_reference", "signed_at"}
        if set(changes) - allowed: raise ValidationError("unknown contract fields")
        if "status" in changes: changes["status"] = enum(changes["status"], "status", {"draft", "pending", "active", "expired", "terminated", "renewed"})
        if changes.get("effective_until") and changes["effective_until"] <= row["effective_from"]: raise ValidationError("contract period is invalid")
        row.update(changes)
        with self.repository.transaction(): self.repository.put("tenant_contracts", contract_id, row); self._audit(ctx, row["tenant_id"], "contract.updated", "tenant_contract", contract_id); return row

    def renew_contract(self, ctx, contract_id, *, contract_number, effective_from, effective_until=None, document_reference=None):
        old = self._tenant_child(ctx, "tenant_contracts", "contract_id", contract_id, "tenants:contract:write")
        if effective_from <= old["effective_from"]: raise ValidationError("renewal must start after the original contract")
        new = self.create_contract(ctx, old["tenant_id"], contract_number=contract_number, status="active", effective_from=effective_from, effective_until=effective_until, document_reference=document_reference)
        self.update_contract(ctx, contract_id, status="renewed", effective_until=old["effective_until"] or effective_from)
        return new

    def get_billing(self, ctx, tenant_id): self._scope(ctx, tenant_id, "tenants:billing:read"); return self.repository.require("tenant_billing_settings", tenant_id)
    def save_billing(self, ctx, tenant_id, **data):
        self._scope(ctx, tenant_id, "tenants:billing:write"); day = int(data.get("billing_day", 1)); terms = int(data.get("payment_terms_days", 0));
        if not 1 <= day <= 31 or terms < 0: raise ValidationError("invalid billing day or payment terms")
        row = {"tenant_id": tenant_id, "billing_currency": required(data.get("billing_currency"), "billing_currency").upper(), "tax_condition": required(data.get("tax_condition"), "tax_condition"), "billing_email": required(data.get("billing_email"), "billing_email").lower(), "billing_day": day, "payment_terms_days": terms, "created_at": utcnow(), "updated_at": utcnow(), "version": 1}
        with self.repository.transaction():
            old=self.repository.get("tenant_billing_settings", tenant_id); row["created_at"] = old["created_at"] if old else row["created_at"]; row["version"] = old["version"]+1 if old else 1; self.repository.put("tenant_billing_settings", tenant_id, row); self._audit(ctx, tenant_id, "billing.updated", "tenant_billing_settings", tenant_id)
        return row
