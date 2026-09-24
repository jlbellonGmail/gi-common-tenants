# Changelog

## [0.1.1] - Preparada para HITL

- Privilegios PostgreSQL mínimos para `authenticated` y `service_role`.
- Sin acceso para `anon`.
- RLS tenant-scoped y lectura de catálogo activo conservados.
- Validación real de aislamiento en Supabase gi-dev.

## [0.1.0] - Preparada para HITL

- Administración administrativa, legal, comercial, contractual y de suscripciones.
- Persistencia PostgreSQL/Supabase con migración reproducible, RLS e integridad entre tenants.
- Historial de condiciones de suscripción y auditoría administrativa.
- Contratos Python con GI-PLATFORM-CORE v0.3.0.
- Adaptador HTTP alineado con las rutas de identidad `/v1/tenants` publicadas por Core.
- CI con pruebas de producto y PostgreSQL real.

La versión no está publicada: no existe tag ni release GitHub.
