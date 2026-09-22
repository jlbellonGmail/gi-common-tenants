from fastapi.testclient import TestClient

from gi_common_tenants.api import create_app
from gi_common_tenants.authorization import TenantContext
from gi_common_tenants.core import CoreApiAdapter, HttpCoreAdapter
from gi_common_tenants.errors import CapabilityUnavailableError
from gi_common_tenants.memory import InMemoryTenantRepository
from gi_common_tenants.service import TenantService


class Core:
    def authorize(self, user_id, tenant_id, permission, location_id=None):
        return {"contract_version": "0.3.0", "allowed": True, "context": {"user_id": user_id, "tenant_id": tenant_id}}
    def list_tenants(self, user_id):
        return [{"tenant_id": "00000000-0000-0000-0000-000000000001"}, {"tenant_id": "00000000-0000-0000-0000-000000000002"}]


def test_http_api_exposes_openapi_and_denies_cross_tenant_context():
    service = TenantService(InMemoryTenantRepository(), Core())
    app = create_app(service, authenticate=lambda request: TenantContext("u", "mine"))
    client = TestClient(app)
    assert client.get("/healthz").status_code == 200
    assert client.get("/openapi.json").status_code == 200
    response = client.get("/v1/tenants/other/profile", headers={"X-User-Id": "u", "X-Tenant-Id": "mine"})
    assert response.status_code == 403


def test_http_adapter_rejects_unpublished_capability():
    adapter = HttpCoreAdapter("http://127.0.0.1:9", "test")
    try:
        adapter.authorize("u", "t", "tenants:profile:read")
    except CapabilityUnavailableError:
        pass
    else:
        raise AssertionError("unpublished HTTP authorization must fail closed")


def test_python_adapter_validates_core_contract():
    class Api:
        def create_tenant(self, name): return {"contract_version": "0.3.0", "id": "t"}
        def list_tenants(self, user_id): return [{"contract_version": "0.3.0", "id": "t"}]
    adapter = CoreApiAdapter(Api())
    assert adapter.create_tenant("ACME")["tenant_id"] == "t"
