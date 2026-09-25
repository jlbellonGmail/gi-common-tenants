# Evidencia de validación

- Fuente: `pyproject.toml` y `gi_common_tenants.__version__` reportan `0.1.2`.
- Wheel: `runs/10-package-version-consistency-v012/artifacts/gi_common_tenants-0.1.2-py3-none-any.whl`.
- SHA-256 del wheel: `BD3E4E1C12C26ED6151A37C9BB6D4718C7F3E85F6873B98E0801DD4A87FD1129`.
- Entorno virtual limpio con dependencias instaladas: metadata `0.1.2`,
  módulo `0.1.2`, APIs `TenantContext`, `TenantService`, `TenantsError` y
  `TenantsApi` importadas correctamente.
- `pytest -q tests_tenants` en entorno virtual limpio: `12 passed, 1 skipped`;
  el skip local es PostgreSQL/RLS por ausencia de `DATABASE_URL`.
- La ejecución global fue descartada por detectar la instalación histórica
  `gi-common-tenants 0.1.1`.
- La suite completa local quedó detenida en una prueba de sincronización de
  adaptadores; el CI remoto la verificó correctamente.
- HEAD definitivo de PR #12: `6609ea552e47d6f49a46d3c56913f265a9e16dc9`.
- CI de PR #12, run `36078388932`: `circuit-tests`, `product-tests` y
  `local-reconciler-tests` PASS.
- `check-integrity.ps1`, `feature-contract`, `sync-agentic-adapters -Check`,
  `validate-supply-chain` y `git diff --check`: PASS.
- `v0.1.1` no fue modificada ni sobrescrita.
