from gi_common_tenants.authorization import TenantContext
from gi_common_tenants.errors import ConflictError, IsolationError
from gi_common_tenants.memory import InMemoryTenantRepository
from gi_common_tenants.service import TenantService


class Core:
    def __init__(self):
        self.created = 0

    def authorize(self, user_id, tenant_id, permission, location_id=None):
        return {"contract_version": "0.3.0", "allowed": True, "context": {"user_id": user_id, "tenant_id": tenant_id}}
    def list_tenants(self, user_id):
        return [{"tenant_id": "00000000-0000-0000-0000-000000000001"}, {"tenant_id": "00000000-0000-0000-0000-000000000002"}]

    def create_tenant(self, name):
        self.created += 1
        return {"contract_version": "0.3.0", "id": "00000000-0000-0000-0000-000000000001", "tenant_id": "00000000-0000-0000-0000-000000000001"}


def service():
    return TenantService(InMemoryTenantRepository(), Core())


def ctx(tenant="00000000-0000-0000-0000-000000000001"):
    return TenantContext("user-1", tenant)


def test_profile_identifier_contact_address_and_audit_are_scoped():
    svc = service(); context = ctx()
    profile = svc.create_profile(context, tenant_id=context.tenant_id, display_name="ACME", legal_name="ACME SA", entity_type="legal_entity", country_code="AR")
    assert profile["tenant_id"] == context.tenant_id
    identifier = svc.add_identifier(context, context.tenant_id, country_code="AR", identifier_type="cuit", identifier_value="30-12345678-9", is_primary=True)
    svc.add_contact(context, context.tenant_id, contact_name="Ana", contact_role="billing", email="ANA@EXAMPLE.COM", is_primary=True)
    svc.add_address(context, context.tenant_id, address_type="tax", address_line1="Calle 1", city="CABA", country_code="AR", is_primary=True)
    assert svc.list_identifiers(context, context.tenant_id)[0]["normalized_value"] == "30123456789"
    assert svc.repository.list("audit_events", tenant_id=context.tenant_id)
    svc.delete_identifier(context, identifier["identifier_id"])


def test_cross_tenant_access_is_denied_before_repository_lookup():
    svc = service(); context = ctx()
    svc.create_profile(context, tenant_id=context.tenant_id, display_name="ACME", legal_name="ACME SA", entity_type="legal_entity", country_code="AR")
    try:
        svc.get_profile(ctx("00000000-0000-0000-0000-000000000002"), context.tenant_id)
    except IsolationError:
        pass
    else:
        raise AssertionError("cross-tenant access must fail closed")


def test_subscription_keeps_price_snapshot_and_rejects_duplicate_active_plan():
    svc = service(); context = ctx()
    svc.create_profile(context, tenant_id=context.tenant_id, display_name="ACME", legal_name="ACME SA", entity_type="legal_entity", country_code="AR")
    plan = svc.save_plan(context, code="basic", name="Basic")
    price = svc.add_price(context, plan["plan_id"], currency_code="ARS", amount="10.50", billing_interval="month", billing_interval_count=1, effective_from="2026-01-01")
    contract = svc.create_contract(context, context.tenant_id, contract_number="C-1", effective_from="2026-01-01", status="active")
    subscription = svc.create_subscription(context, context.tenant_id, contract_id=contract["contract_id"], plan_id=plan["plan_id"], price_id=price["price_id"], started_at="2026-01-01", current_period_start="2026-01-01", current_period_end="2026-02-01", status="active")
    assert subscription["price_snapshot"]["amount"] == "10.50"
    try:
        svc.create_subscription(context, context.tenant_id, contract_id=contract["contract_id"], plan_id=plan["plan_id"], price_id=price["price_id"], started_at="2026-02-01", current_period_start="2026-02-01", current_period_end="2026-03-01", status="active")
    except ConflictError:
        pass
    else:
        raise AssertionError("duplicate active plan must fail")
