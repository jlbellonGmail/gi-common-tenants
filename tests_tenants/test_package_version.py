from importlib.metadata import version
import gi_common_tenants

def test_public_module_version_matches_distribution_metadata():
    assert gi_common_tenants.__version__ == "0.1.1"
    assert version("gi-common-tenants") == "0.1.1"
    assert gi_common_tenants.TenantContext
    assert gi_common_tenants.TenantService
    assert gi_common_tenants.TenantsError
