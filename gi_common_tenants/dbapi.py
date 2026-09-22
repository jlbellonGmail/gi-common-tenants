"""PostgreSQL repository using caller-owned psycopg connections."""

import json
from contextlib import contextmanager
from uuid import uuid4

from .errors import ConflictError, NotFoundError, VersionConflictError


TABLES = {
    "tenant_profiles": ("tenant_id", ("tenant_id", "display_name", "legal_name", "entity_type", "country_code", "locale", "timezone", "version", "created_at", "updated_at")),
    "tenant_identifiers": ("identifier_id", ("identifier_id", "tenant_id", "country_code", "identifier_type", "identifier_value", "normalized_value", "is_primary", "created_at")),
    "tenant_contacts": ("contact_id", ("contact_id", "tenant_id", "contact_name", "contact_role", "email", "phone", "is_primary", "created_at", "updated_at")),
    "tenant_addresses": ("address_id", ("address_id", "tenant_id", "address_type", "address_line1", "address_line2", "city", "region", "postal_code", "country_code", "is_primary", "created_at", "updated_at")),
    "service_plans": ("plan_id", ("plan_id", "code", "name", "description", "is_active", "created_at", "updated_at")),
    "service_plan_prices": ("price_id", ("price_id", "plan_id", "currency_code", "amount", "billing_interval", "billing_interval_count", "effective_from", "effective_until", "is_active", "created_at", "updated_at")),
    "service_plan_entitlements": ("entitlement_id", ("entitlement_id", "plan_id", "entitlement_code", "entitlement_type", "entitlement_value", "effective_from", "effective_until", "created_at", "updated_at")),
    "tenant_contracts": ("contract_id", ("contract_id", "tenant_id", "contract_number", "status", "signed_at", "effective_from", "effective_until", "document_reference", "created_at")),
    "tenant_subscriptions": ("subscription_id", ("subscription_id", "tenant_id", "contract_id", "plan_id", "price_id", "status", "started_at", "current_period_start", "current_period_end", "cancel_at", "canceled_at", "created_at", "updated_at", "version", "price_snapshot")),
    "tenant_billing_settings": ("tenant_id", ("tenant_id", "billing_currency", "tax_condition", "billing_email", "billing_day", "payment_terms_days", "created_at", "updated_at", "version")),
}
JSON_FIELDS = {"entitlement_value", "price_snapshot"}


class PostgresTenantRepository:
    def __init__(self, connection_factory, *, schema="tenants"):
        self.connection_factory, self.schema = connection_factory, schema
        self._active = None
        self._context = None

    def new_id(self): return str(uuid4())
    def set_context(self, tenant_id: str, user_id: str) -> None:
        self._context = (str(tenant_id), str(user_id))
    @contextmanager
    def transaction(self):
        connection = self.connection_factory(); self._active = connection
        try:
            self._set_context(connection)
            with connection: yield self
        finally: self._active = None; connection.close()

    def _set_context(self, connection):
        if self._context is None:
            return
        with connection.cursor() as cur:
            cur.execute("select set_config('app.tenant_id', %s, true), set_config('app.user_id', %s, true)", self._context)

    @contextmanager
    def _connection(self):
        if self._active is not None: yield self._active; return
        connection = self.connection_factory()
        try:
            self._set_context(connection)
            yield connection
        finally: connection.close()

    def _query(self, sql, params=()):
        with self._connection() as conn:
            with conn.cursor() as cur: cur.execute(sql, params); return cur.fetchall()

    def get(self, table, key):
        pk, columns = TABLES[table]
        rows = self._query(f"select {', '.join(columns)} from {self.schema}.{table} where {pk} = %s", (str(key),))
        return self._row(columns, rows[0]) if rows else None
    def require(self, table, key):
        row = self.get(table, key)
        if row is None: raise NotFoundError()
        return row
    def list(self, table, *, tenant_id=None, filters=None):
        pk, columns = TABLES[table]; clauses=[]; params=[]
        if tenant_id is not None and "tenant_id" in columns: clauses.append("tenant_id = %s"); params.append(str(tenant_id))
        for field, value in (filters or {}).items(): clauses.append(f"{field} = %s"); params.append(value)
        where = " where " + " and ".join(clauses) if clauses else ""
        rows = self._query(f"select {', '.join(columns)} from {self.schema}.{table}{where} order by {pk}", params)
        return [self._row(columns, row) for row in rows]
    def put(self, table, key, value, *, expected_version=None):
        pk, columns = TABLES[table]; data={field:value.get(field) for field in columns if field in value}
        if expected_version is not None:
            current=self.get(table,key)
            if current is None or current.get("version") != expected_version: raise VersionConflictError()
            data["version"] = expected_version+1
        fields=list(data); placeholders=", ".join(["%s"]*len(fields)); updates=", ".join(f"{f}=excluded.{f}" for f in fields if f != pk)
        params=[json.dumps(v) if f in JSON_FIELDS and v is not None else v for f,v in data.items()]
        with self._connection() as conn:
            try:
                with conn.cursor() as cur: cur.execute(f"insert into {self.schema}.{table} ({', '.join(fields)}) values ({placeholders}) on conflict ({pk}) do update set {updates} returning {', '.join(columns)}", params); row=cur.fetchone()
            except Exception as exc:
                if "unique" in str(exc).lower(): raise ConflictError() from exc
                raise
        return self._row(columns,row)
    def delete(self, table, key):
        pk,_=TABLES[table]
        with self._connection() as conn:
            with conn.cursor() as cur: cur.execute(f"delete from {self.schema}.{table} where {pk}=%s", (str(key),))
    def unique(self, table, fields, value, *, ignore_id=None):
        clauses=" and ".join(f"{field}=%s" for field in fields); params=[value.get(field) for field in fields]
        rows=self._query(f"select 1 from {self.schema}.{table} where {clauses} limit 1", params)
        if rows: raise ConflictError()
    def record_audit(self, event):
        with self._connection() as conn:
            with conn.cursor() as cur: cur.execute(f"insert into {self.schema}.audit_events (event_id,tenant_id,actor_user_id,action,resource,resource_id,outcome,occurred_at) values (%s,%s,%s,%s,%s,%s,%s,%s)", tuple(event.get(k) for k in ("event_id","tenant_id","actor_user_id","action","resource","resource_id","outcome","occurred_at")))
    @staticmethod
    def _row(columns, row):
        result=dict(zip(columns,row))
        for field in JSON_FIELDS:
            if field in result and isinstance(result[field], str): result[field]=json.loads(result[field])
        return result
