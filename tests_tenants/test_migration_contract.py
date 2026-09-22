from pathlib import Path


MIGRATION = Path(__file__).parents[1] / "supabase" / "migrations" / "20260922000000_tenants_initial.sql"


def test_migration_defines_all_owned_tables_without_core_foreign_keys():
    sql = MIGRATION.read_text(encoding="utf-8").lower()
    for table in (
        "tenant_profiles", "tenant_identifiers", "tenant_contacts", "tenant_addresses",
        "service_plans", "service_plan_prices", "service_plan_entitlements",
        "tenant_contracts", "tenant_subscriptions", "tenant_billing_settings",
    ):
        assert f"create table if not exists tenants.{table}" in sql
    assert "references core." not in sql
    assert "enable row level security" in sql
    assert "price_snapshot jsonb not null" in sql
