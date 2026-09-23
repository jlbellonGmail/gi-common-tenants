"""Integration coverage against the checked-in public Core HTTP contract."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from threading import Thread
from wsgiref.simple_server import make_server

import pytest

CORE_PATH = Path(
    os.environ.get("GI_PLATFORM_CORE_PATH", r"C:\Proyectos\gi-platform-core")
)
if not CORE_PATH.exists():
    pytest.skip(
        "GI-PLATFORM-CORE checkout not available in this runner",
        allow_module_level=True,
    )
sys.path.insert(0, str(CORE_PATH))

from gi_platform_core.adapters import InMemoryCoreStore
from gi_platform_core.application import CoreService
from gi_platform_core.contracts import CoreApi
from gi_platform_core.http import AuthenticatedActor, create_app

from gi_common_tenants.core import HttpCoreAdapter


def test_real_core_v020_http_contract_validates_identity() -> None:
    api = CoreApi(CoreService(InMemoryCoreStore()))
    organization = api.create_tenant("HTTP integration tenant")
    user = api.create_user("http-subject", "HTTP user")
    api.add_membership(user["id"], organization["id"])

    def authenticate(_headers: dict[str, str]) -> AuthenticatedActor:
        return AuthenticatedActor(user["id"], tenant_id=organization["tenant_id"])

    server = make_server("127.0.0.1", 0, create_app(api, authenticate))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        adapter = HttpCoreAdapter(
            f"http://127.0.0.1:{server.server_port}",
            "integration-token",
        )
        result = adapter.validate_identity(
            organization["tenant_id"], user["id"], "http-subject"
        )
        assert result["contract_version"] == "0.2.0"
        assert result["valid"] is True
        assert result["user"]["id"] == user["id"]
    finally:
        server.shutdown()
        thread.join(timeout=5)
