# API de Common-Tenants

La API HTTP se crea con `gi_common_tenants.api.create_app`. Todas las rutas
requieren contexto autenticado del host y vuelven a validar autorización en
Core. Las respuestas de error son `{ "error": { "code", "message", "details" } }`.

Ejemplo conceptual:

```http
POST /v1/tenants/7c.../contracts
X-User-Id: user-from-host
X-Tenant-Id: 7c...
Content-Type: application/json

{"contract_number":"GI-2026-001","effective_from":"2026-09-22","status":"active"}
```

En producción los headers anteriores deben ser derivados por un adaptador de
autenticación confiable, no aceptados directamente de un cliente externo.
OpenAPI generado por FastAPI está disponible en `/openapi.json` y `/docs`.
