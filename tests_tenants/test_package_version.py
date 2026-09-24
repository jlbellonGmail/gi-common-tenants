from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import tomllib
import gi_common_tenants

def test_public_module_version_matches_distribution_metadata():
    assert gi_common_tenants.__version__ == "0.1.1"
    try:
        installed_version = version("gi-common-tenants")
    except PackageNotFoundError:
        with (Path(__file__).parents[1] / "pyproject.toml").open("rb") as handle:
            installed_version = tomllib.load(handle)["project"]["version"]
    assert installed_version == "0.1.1"
    assert gi_common_tenants.TenantContext
    assert gi_common_tenants.TenantService
    assert gi_common_tenants.TenantsError
