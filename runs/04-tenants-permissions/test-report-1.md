status: approved
attempt: 1
feedback:
  - `pytest -q tests_tenants --ignore=tests_tenants/test_postgres_integration.py`: 11 passed.
  - PostgreSQL gi-dev: migración 20260924000000 aplicada y registrada.
  - RLS activo en 12 tablas; `authenticated` ve sólo el tenant de su contexto.
  - Insert cross-tenant rechazado por RLS.
  - Escritura de catálogo por `authenticated` rechazada.
  - `anon` sin privilegios; `service_role` con privilegios backend.
  - core conserva 10 tablas y no fue modificado.
