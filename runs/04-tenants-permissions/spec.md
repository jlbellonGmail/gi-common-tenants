# Especificación

- `anon` no recibe permisos sobre `tenants`.
- `authenticated` recibe DML sólo sobre tablas tenant-scoped; RLS limita por
  `app.tenant_id`.
- `authenticated` sólo lee el catálogo; no puede administrarlo.
- `service_role` es backend-only y recibe privilegios de servicio.
- Las tablas de auditoría e historial permanecen bajo control del backend.
- No se modifica `core`.
