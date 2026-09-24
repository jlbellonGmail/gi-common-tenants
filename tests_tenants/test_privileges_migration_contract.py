from pathlib import Path


SQL = (Path(__file__).parents[1] / "supabase" / "migrations" / "20260924000000_tenants_privileges.sql").read_text(encoding="utf-8").lower()


def test_privileges_migration_keeps_anonymous_role_out_and_grants_backend():
    assert "grant usage on schema tenants to authenticated, service_role" in SQL
    assert "grant all privileges on all tables in schema tenants to service_role" in SQL
    assert "grant select, insert, update, delete" in SQL
    assert "to anon" not in SQL


def test_privileges_migration_keeps_catalog_writes_backend_only():
    assert "grant select on" in SQL
    assert "service_plan_prices" in SQL
    assert "service_plan_entitlements" in SQL
    assert "alter default privileges in schema tenants" in SQL
    assert "create policy catalog_read on tenants.service_plan_entitlements" in SQL
