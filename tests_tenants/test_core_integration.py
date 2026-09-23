import sys
from pathlib import Path

import pytest

CORE_PATH = Path(r"C:\Proyectos\gi-platform-core")
if not CORE_PATH.exists():
    pytest.skip("GI-PLATFORM-CORE checkout not available in this runner", allow_module_level=True)
sys.path.insert(0, str(CORE_PATH))

from gi_platform_core import CoreApi, CoreService, InMemoryCoreStore
from gi_common_tenants.core import CoreApiAdapter
from gi_common_tenants.authorization import TenantContext
from gi_common_tenants.memory import InMemoryTenantRepository
from gi_common_tenants.service import TenantService


def test_real_core_v030_python_contract_authorizes_common_tenants():
    core_service = CoreService(InMemoryCoreStore())
    core_service.create_permission("tenants:profile:write", "Write tenant profile")
    core = CoreApi(core_service)
    tenant = core.create_tenant("ACME")
    user = core.create_user("subject-1", "Admin")
    membership = core.add_membership(user["id"], tenant["tenant_id"])
    role = core.create_role(tenant["tenant_id"], "tenant-admin", {"tenants:profile:write"})
    core.assign_role(membership["id"], role["id"])

    service = TenantService(InMemoryTenantRepository(), CoreApiAdapter(core))
    context = TenantContext(user["id"], tenant["tenant_id"])
    profile = service.create_profile(context, tenant_id=tenant["tenant_id"], display_name="ACME", legal_name="ACME SA", entity_type="legal_entity", country_code="AR")
    assert profile["tenant_id"] == tenant["tenant_id"]
