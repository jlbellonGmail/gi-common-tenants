status: approved
attempt: 2
feedback:
  - "PASS: la rama release/v0.1.2 deriva de develop y contiene main como ancestro mediante un merge normal; no hay force-push ni alteración de main."
  - "PASS: release-readiness.ps1 valida ramas de release descendientes de develop, conserva la comprobación de origin/develop y tiene regresión en tests/test_release_readiness.py."
  - "PASS: el diff vigente mantiene pyproject.toml y gi_common_tenants.__version__ en 0.1.2, conserva v0.1.1 y no publica en PyPI."
  - "PASS: CI remoto del HEAD vigente y check-integrity son requisitos previos a la autorización HITL."
