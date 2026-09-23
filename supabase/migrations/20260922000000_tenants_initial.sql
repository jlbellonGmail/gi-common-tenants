-- GI-COMMON-TENANTS v0.1.0
-- Owns administrative/commercial data only. tenant_id is an opaque reference
-- to core.tenants; no foreign key reaches Core's private schema.
create extension if not exists btree_gist;
create schema if not exists tenants;

create table if not exists tenants.tenant_profiles (
  tenant_id uuid primary key,
  display_name text not null check (length(btrim(display_name)) > 0),
  legal_name text not null check (length(btrim(legal_name)) > 0),
  entity_type text not null check (entity_type in ('individual','legal_entity')),
  country_code text not null check (country_code ~ '^[A-Z]{2}$'),
  locale text not null,
  timezone text not null,
  version bigint not null default 1 check (version > 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists tenants.tenant_identifiers (
  identifier_id uuid primary key default gen_random_uuid(), tenant_id uuid not null,
  country_code text not null check (country_code ~ '^[A-Z]{2}$'), identifier_type text not null,
  identifier_value text not null, normalized_value text not null, is_primary boolean not null default false,
  created_at timestamptz not null default now(),
  unique (tenant_id, country_code, identifier_type, normalized_value)
);
create unique index if not exists tenant_identifiers_one_primary on tenants.tenant_identifiers(tenant_id) where is_primary;

create table if not exists tenants.tenant_contacts (
  contact_id uuid primary key default gen_random_uuid(), tenant_id uuid not null,
  contact_name text not null, contact_role text not null, email text, phone text,
  is_primary boolean not null default false, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create unique index if not exists tenant_contacts_one_primary_role on tenants.tenant_contacts(tenant_id, contact_role) where is_primary;

create table if not exists tenants.tenant_addresses (
  address_id uuid primary key default gen_random_uuid(), tenant_id uuid not null,
  address_type text not null check (address_type in ('legal','tax','commercial','mailing')),
  address_line1 text not null, address_line2 text, city text not null, region text, postal_code text,
  country_code text not null check (country_code ~ '^[A-Z]{2}$'), is_primary boolean not null default false,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create unique index if not exists tenant_addresses_one_primary_type on tenants.tenant_addresses(tenant_id, address_type) where is_primary;

create table if not exists tenants.service_plans (
  plan_id uuid primary key default gen_random_uuid(), code text not null unique, name text not null,
  description text, is_active boolean not null default true, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists tenants.service_plan_prices (
  price_id uuid primary key default gen_random_uuid(), plan_id uuid not null references tenants.service_plans(plan_id),
  currency_code text not null check (currency_code ~ '^[A-Z]{3}$'), amount numeric(19,4) not null check (amount >= 0),
  billing_interval text not null check (billing_interval in ('day','week','month','year')), billing_interval_count integer not null check (billing_interval_count > 0),
  effective_from date not null, effective_until date, is_active boolean not null default true,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  check (effective_until is null or effective_until > effective_from),
  unique (plan_id, price_id),
  unique (plan_id, currency_code, billing_interval, billing_interval_count, effective_from)
);
alter table tenants.service_plan_prices drop constraint if exists service_plan_prices_no_overlap;
alter table tenants.service_plan_prices add constraint service_plan_prices_no_overlap
  exclude using gist (plan_id with =, currency_code with =, billing_interval with =,
    billing_interval_count with =,
    daterange(effective_from, coalesce(effective_until, 'infinity'::date), '[)') with &&);
create table if not exists tenants.service_plan_entitlements (
  entitlement_id uuid primary key default gen_random_uuid(), plan_id uuid not null references tenants.service_plans(plan_id),
  entitlement_code text not null check (entitlement_code ~ '^[a-z][a-z0-9_.-]*$'), entitlement_type text not null check (entitlement_type in ('module','feature','limit','quantity')),
  entitlement_value jsonb not null, effective_from date not null, effective_until date,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  check (effective_until is null or effective_until > effective_from), unique (plan_id, entitlement_code, effective_from)
);

create table if not exists tenants.tenant_contracts (
  contract_id uuid primary key default gen_random_uuid(), tenant_id uuid not null, contract_number text not null unique,
  status text not null check (status in ('draft','pending','active','expired','terminated','renewed')),
  signed_at timestamptz, effective_from date not null, effective_until date, document_reference text,
  created_at timestamptz not null default now(), check (effective_until is null or effective_until > effective_from),
  unique (tenant_id, contract_id)
);
create table if not exists tenants.tenant_subscriptions (
  subscription_id uuid primary key default gen_random_uuid(), tenant_id uuid not null,
  contract_id uuid not null, plan_id uuid not null references tenants.service_plans(plan_id), price_id uuid not null,
  status text not null check (status in ('pending','active','canceled','expired','past_due')),
  started_at date not null, current_period_start date not null, current_period_end date not null,
  cancel_at date, canceled_at timestamptz, created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  version bigint not null default 1 check (version > 0), price_snapshot jsonb not null,
  check (current_period_end > current_period_start), check (cancel_at is null or cancel_at >= current_period_start),
  constraint tenant_subscriptions_contract_tenant_fk foreign key (tenant_id, contract_id)
    references tenants.tenant_contracts(tenant_id, contract_id),
  constraint tenant_subscriptions_plan_price_fk foreign key (plan_id, price_id)
    references tenants.service_plan_prices(plan_id, price_id)
);
create unique index if not exists tenant_subscriptions_one_active_plan on tenants.tenant_subscriptions(tenant_id, plan_id) where status = 'active';
create table if not exists tenants.tenant_billing_settings (
  tenant_id uuid primary key, billing_currency text not null check (billing_currency ~ '^[A-Z]{3}$'), tax_condition text not null,
  billing_email text not null, billing_day integer not null check (billing_day between 1 and 31), payment_terms_days integer not null check (payment_terms_days >= 0),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(), version bigint not null default 1 check (version > 0)
);
create table if not exists tenants.audit_events (
  event_id uuid primary key default gen_random_uuid(), tenant_id uuid, actor_user_id uuid, action text not null,
  resource text not null, resource_id text not null, outcome text not null, occurred_at timestamptz not null default now()
);
create table if not exists tenants.tenant_subscription_history (
  history_id uuid primary key default gen_random_uuid(), subscription_id uuid not null,
  tenant_id uuid not null, event_type text not null, previous_state jsonb,
  new_state jsonb not null, occurred_at timestamptz not null default now()
);

create index if not exists tenant_identifiers_tenant_idx on tenants.tenant_identifiers(tenant_id);
create index if not exists tenant_contacts_tenant_idx on tenants.tenant_contacts(tenant_id);
create index if not exists tenant_addresses_tenant_idx on tenants.tenant_addresses(tenant_id);
create index if not exists tenant_contracts_tenant_idx on tenants.tenant_contracts(tenant_id, effective_from desc);
create index if not exists tenant_subscriptions_tenant_idx on tenants.tenant_subscriptions(tenant_id, status);
create index if not exists audit_events_tenant_time_idx on tenants.audit_events(tenant_id, occurred_at desc);
create index if not exists tenant_subscription_history_tenant_time_idx on tenants.tenant_subscription_history(tenant_id, occurred_at desc);

create or replace function tenants.current_tenant_id() returns uuid language sql stable as $$
  select nullif(current_setting('app.tenant_id', true), '')::uuid
$$;
do $$ declare table_name text; begin
  foreach table_name in array array['tenant_profiles','tenant_identifiers','tenant_contacts','tenant_addresses','tenant_contracts','tenant_subscriptions','tenant_billing_settings','audit_events'] loop
    execute format('alter table tenants.%I enable row level security', table_name);
    execute format('drop policy if exists tenant_isolation on tenants.%I', table_name);
    execute format('create policy tenant_isolation on tenants.%I using (tenant_id = tenants.current_tenant_id() or current_user in (''service_role'',''postgres'')) with check (tenant_id = tenants.current_tenant_id() or current_user in (''service_role'',''postgres''))', table_name);
  end loop;
end $$;
alter table tenants.tenant_subscription_history enable row level security;
drop policy if exists tenant_isolation on tenants.tenant_subscription_history;
create policy tenant_isolation on tenants.tenant_subscription_history
  using (tenant_id = tenants.current_tenant_id() or current_user in ('service_role','postgres'))
  with check (tenant_id = tenants.current_tenant_id() or current_user in ('service_role','postgres'));
alter table tenants.service_plans enable row level security;
alter table tenants.service_plan_prices enable row level security;
alter table tenants.service_plan_entitlements enable row level security;
drop policy if exists catalog_read on tenants.service_plans;
drop policy if exists catalog_read on tenants.service_plan_prices;
drop policy if exists catalog_read on tenants.service_plan_entitlements;
create policy catalog_read on tenants.service_plans for select using (is_active or current_user in ('service_role','postgres'));
create policy catalog_read on tenants.service_plan_prices for select using (is_active or current_user in ('service_role','postgres'));
create policy catalog_read on tenants.service_plan_entitlements for select using (current_user in ('service_role','postgres'));
