# Decisión

Se elige `authenticated` para sesiones con contexto RLS y `service_role` para
el backend autorizado. `anon` queda sin acceso. No se concede acceso global a
usuarios finales ni se replica la autorización de Core en PostgreSQL.
