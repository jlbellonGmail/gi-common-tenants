"""GI-COMMON-TENANTS public package."""

__version__ = "0.1.2"

from .authorization import TenantContext
from .core import CoreApiAdapter, HttpCoreAdapter
from .errors import TenantsError
from .memory import InMemoryTenantRepository
from .service import TenantService

__all__ = [
    "CoreApiAdapter",
    "HttpCoreAdapter",
    "InMemoryTenantRepository",
    "TenantContext",
    "TenantService",
    "TenantsError",
    "__version__",
]
