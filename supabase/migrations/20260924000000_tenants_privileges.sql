-- GI-COMMON-TENANTS incremental security migration.
-- The Common-Tenants HTTP/Python service is the authorization boundary.
-- anon receives no access; authenticated is constrained by existing RLS;
-- service_role is backend-only and must never be exposed to clients.

grant usage on schema tenants to authenticated, service_role;

-- Tenant-scoped data: RLS remains the row-level boundary.
grant select, insert, update, delete on
  tenants.tenant_profiles,
  tenants.tenant_identifiers,
  tenants.tenant_contacts,
  tenants.tenant_addresses,
  tenants.tenant_contracts,
  tenants.tenant_subscriptions,
  tenants.tenant_billing_settings
to authenticated;

-- Catalog data is readable, but catalog administration stays backend-only.
grant select on
  tenants.service_plans,
  tenants.service_plan_prices,
  tenants.service_plan_entitlements
to authenticated;

-- Audit and subscription history are append-only service concerns.
grant all privileges on all tables in schema tenants to service_role;
grant usage, select on all sequences in schema tenants to service_role;

drop policy if exists catalog_read on tenants.service_plan_entitlements;
create policy catalog_read on tenants.service_plan_entitlements
  for select
  using (
    (
      effective_from <= current_date
      and (effective_until is null or effective_until > current_date)
    )
    or current_user in ('service_role', 'postgres')
  );

-- Keep future service-owned tables usable without broadening client access.
alter default privileges in schema tenants
  grant all privileges on tables to service_role;
alter default privileges in schema tenants
  grant usage, select on sequences to service_role;
