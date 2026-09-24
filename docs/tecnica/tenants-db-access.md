# Acceso PostgreSQL de Common-Tenants

El servicio valida identidad y permisos mediante GI-PLATFORM-CORE antes de
usar `PostgresTenantRepository`. La base de datos no recibe credenciales de
usuarios finales.

- `anon`: sin uso sobre `tenants`.
- `authenticated`: uso del esquema y DML sólo sobre datos tenant-scoped; las
  políticas RLS limitan las filas al `app.tenant_id` de la sesión. Puede leer
  el catálogo activo, pero no administrarlo.
- `service_role`: reservado al backend y con privilegios de servicio. Nunca
  se expone al cliente ni reemplaza la autorización de Core.
- `postgres`: sólo bootstrap/operación controlada; no representa a un usuario.

La política incremental está en
`supabase/migrations/20260924000000_tenants_privileges.sql`. La migración no
modifica `core`, no concede permisos a `anon` y conserva RLS en las doce
tablas.
