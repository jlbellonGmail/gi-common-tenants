"""Real PostgreSQL migration, RLS and cross-tenant integrity checks."""

from pathlib import Path
import os

import pytest

psycopg = pytest.importorskip("psycopg")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    pytest.skip("DATABASE_URL no configurada; se requiere PostgreSQL real", allow_module_level=True)

MIGRATION = (Path(__file__).parents[1] / "supabase" / "migrations" / "20260922000000_tenants_initial.sql").read_text(encoding="utf-8")


def test_postgres_schema_rls_and_tenant_integrity():
    with psycopg.connect(DATABASE_URL, autocommit=True) as connection:
        connection.execute("drop schema if exists tenants cascade")
        connection.execute(MIGRATION)
        tables = connection.execute(
            "select count(*) from information_schema.tables where table_schema = 'tenants'"
        ).fetchone()[0]
        assert tables == 12
        rls = connection.execute(
            "select count(*) from pg_tables where schemaname = 'tenants' and rowsecurity"
        ).fetchone()[0]
        assert rls == 12

        connection.execute("drop role if exists tenants_integration_app")
        connection.execute("create role tenants_integration_app login password 'integration'")
        connection.execute("grant usage on schema tenants to tenants_integration_app")
        connection.execute("grant select, insert, update, delete on all tables in schema tenants to tenants_integration_app")
        connection.execute("grant usage, select on all sequences in schema tenants to tenants_integration_app")
        connection.execute(
            "insert into tenants.tenant_profiles "
            "(tenant_id, display_name, legal_name, entity_type, country_code, locale, timezone) "
            "values (%s, 'Tenant A', 'Tenant A', 'legal_entity', 'AR', 'es-AR', 'UTC'), "
            "(%s, 'Tenant B', 'Tenant B', 'legal_entity', 'AR', 'es-AR', 'UTC')",
            ("00000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000002"),
        )
        connection.execute(
            "insert into tenants.service_plans(plan_id, code, name) values (%s, 'a', 'A'), (%s, 'b', 'B')",
            ("10000000-0000-0000-0000-000000000001", "10000000-0000-0000-0000-000000000002"),
        )
        connection.execute(
            "insert into tenants.service_plan_prices(price_id, plan_id, currency_code, amount, billing_interval, billing_interval_count, effective_from) "
            "values (%s, %s, 'ARS', 10, 'month', 1, '2026-01-01'), (%s, %s, 'ARS', 20, 'month', 1, '2026-01-01')",
            ("20000000-0000-0000-0000-000000000001", "10000000-0000-0000-0000-000000000001", "20000000-0000-0000-0000-000000000002", "10000000-0000-0000-0000-000000000002"),
        )
        connection.execute(
            "insert into tenants.tenant_contracts(contract_id, tenant_id, contract_number, status, effective_from) "
            "values (%s, %s, 'A-1', 'active', '2026-01-01'), (%s, %s, 'B-1', 'active', '2026-01-01')",
            ("30000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000001", "30000000-0000-0000-0000-000000000002", "00000000-0000-0000-0000-000000000002"),
        )
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            connection.execute(
                "insert into tenants.tenant_subscriptions(subscription_id, tenant_id, contract_id, plan_id, price_id, status, started_at, current_period_start, current_period_end, price_snapshot) "
                "values (%s, %s, %s, %s, %s, 'active', '2026-01-01', '2026-01-01', '2026-02-01', '{}')",
                ("40000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000001", "30000000-0000-0000-0000-000000000002", "10000000-0000-0000-0000-000000000001", "20000000-0000-0000-0000-000000000001"),
            )

    app_url = DATABASE_URL.replace("postgresql://postgres:postgres@", "postgresql://tenants_integration_app:integration@")
    with psycopg.connect(app_url) as app_connection:
        app_connection.execute("select set_config('app.tenant_id', %s, false)", ("00000000-0000-0000-0000-000000000001",))
        assert app_connection.execute("select count(*) from tenants.tenant_profiles").fetchone()[0] == 1
