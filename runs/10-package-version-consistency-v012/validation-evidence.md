# Evidencia de validación

- Fuente: `pyproject.toml` y `gi_common_tenants.__version__` reportan `0.1.2`.
- Wheel: `runs/10-package-version-consistency-v012/artifacts/gi_common_tenants-0.1.2-py3-none-any.whl`.
- SHA-256 del wheel: `BD3E4E1C12C26ED6151A37C9BB6D4718C7F3E85F6873B98E0801DD4A87FD1129`.
- Entorno virtual limpio con dependencias instaladas: metadata `0.1.2`,
  módulo `0.1.2`, APIs `TenantContext`, `TenantService`, `TenantsError` y
  `TenantsApi` importadas correctamente.
- `pytest -q tests_tenants` en entorno virtual limpio: `12 passed, 1 skipped`;
  el skip local es PostgreSQL/RLS porque `DATABASE_URL` no está configurada.
- La primera ejecución con el entorno global fue descartada por detectar la
  instalación histórica `gi-common-tenants 0.1.1`; no se usa como evidencia.
- La suite completa local `tests` no concluyó en este host: quedó detenida en
  la prueba de sincronización de adaptadores después de varias ejecuciones.
  Se conserva como incidencia local y queda exigida/verificada por CI.
- La release/tag `v0.1.1` no fue modificada.
