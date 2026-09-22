"""Deterministic repository for tests and local examples.

It mirrors the PostgreSQL aggregate boundaries and intentionally does not
pretend to test RLS; PostgreSQL tests are separate and require a real server.
"""

from copy import deepcopy
from threading import RLock
from uuid import uuid4

from .errors import ConflictError, NotFoundError, VersionConflictError


class InMemoryTenantRepository:
    def __init__(self):
        self.lock = RLock()
        self.tables = {name: {} for name in (
            "tenant_profiles", "tenant_identifiers", "tenant_contacts", "tenant_addresses",
            "service_plans", "service_plan_prices", "service_plan_entitlements",
            "tenant_contracts", "tenant_subscriptions", "tenant_billing_settings", "audit_events",
        )}

    def transaction(self):
        return _Transaction(self)

    def set_context(self, tenant_id: str, user_id: str) -> None:
        # Memory has no database session; the service still calls this method
        # so the PostgreSQL adapter receives the exact same boundary.
        return None

    def new_id(self) -> str:
        return str(uuid4())

    def get(self, table: str, key: str):
        value = self.tables[table].get(str(key))
        return deepcopy(value) if value is not None else None

    def put(self, table: str, key: str, value: dict, *, expected_version: int | None = None):
        key = str(key)
        current = self.tables[table].get(key)
        if expected_version is not None:
            if current is None or current.get("version") != expected_version:
                raise VersionConflictError()
            value = {**value, "version": expected_version + 1}
        self.tables[table][key] = deepcopy(value)
        return deepcopy(value)

    def delete(self, table: str, key: str):
        self.tables[table].pop(str(key), None)

    def list(self, table: str, *, tenant_id: str | None = None, filters: dict | None = None):
        values = list(self.tables[table].values())
        if tenant_id is not None:
            values = [v for v in values if v.get("tenant_id") == str(tenant_id)]
        for field, expected in (filters or {}).items():
            values = [v for v in values if v.get(field) == expected]
        return deepcopy(values)

    def require(self, table: str, key: str):
        value = self.get(table, key)
        if value is None:
            raise NotFoundError()
        return value

    def unique(self, table: str, fields: tuple[str, ...], value: dict, *, ignore_id: str | None = None):
        for row in self.tables[table].values():
            if ignore_id is not None and str(row.get(self._id_field(table))) == str(ignore_id):
                continue
            if all(row.get(field) == value.get(field) for field in fields):
                raise ConflictError()

    @staticmethod
    def _id_field(table: str) -> str:
        return {
            "tenant_profiles": "tenant_id", "tenant_billing_settings": "tenant_id",
            "tenant_identifiers": "identifier_id", "tenant_contacts": "contact_id",
            "tenant_addresses": "address_id", "service_plans": "plan_id",
            "service_plan_prices": "price_id", "service_plan_entitlements": "entitlement_id",
            "tenant_contracts": "contract_id", "tenant_subscriptions": "subscription_id",
            "audit_events": "event_id",
        }[table]

    def record_audit(self, event: dict):
        self.tables["audit_events"][event["event_id"]] = deepcopy(event)


class _Transaction:
    def __init__(self, repository):
        self.repository = repository
        self.snapshot = None

    def __enter__(self):
        self.repository.lock.acquire()
        self.snapshot = deepcopy(self.repository.tables)
        return self.repository

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.repository.tables = self.snapshot
        self.repository.lock.release()
        return False
