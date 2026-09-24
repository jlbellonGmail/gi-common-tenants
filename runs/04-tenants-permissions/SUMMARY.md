# 04-tenants-permissions

Se agrega la migración incremental `20260924000000_tenants_privileges.sql`
para habilitar sólo los roles necesarios y conservar el aislamiento RLS.
La migración fue aplicada y validada en Supabase gi-dev usando la conexión
transitoria de Core, sin guardar credenciales.

Estado de implementación: listo para revisión independiente y PR.
