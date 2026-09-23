# GI-COMMON-TENANTS

Módulo común de GI para administrar la información administrativa, legal,
fiscal, comercial, contractual y de suscripciones de los clientes que
contratan la plataforma.

## Límites

Core es propietario de la identidad técnica, `tenant_id`, autenticación,
membresías, roles, permisos, sedes y aislamiento. Common-Tenants sólo guarda
datos comerciales y administrativos. No hay tablas ni claves foráneas hacia
las tablas privadas de Core. Persons tampoco es requerido para completar el
alta administrativa.

La integración Python consume `gi-platform-core==0.3.0`. La API HTTP de Core
publicada en `contracts/core-http-v0.2.0.openapi.json` sólo ofrece las
operaciones de identidad; el adaptador HTTP falla cerrado para creación,
listado y autorización hasta que Core publique esos contratos por HTTP.

## Inicio local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

La identidad HTTP de Core v0.3.0 usa `/v1/tenants/{tenant_id}`; las rutas
`organizations` son legacy. El adaptador falla cerrado para creación, listado
y autorización porque esas operaciones sólo están publicadas por Python.

Aplicar la migración `supabase/migrations/20260922000000_tenants_initial.sql`
en PostgreSQL/Supabase. El servicio usa `psycopg` y el repositorio
`PostgresTenantRepository`; no depende de cambios manuales en la base.

## API

```python
from gi_common_tenants import InMemoryTenantRepository, TenantService, TenantContext
from gi_common_tenants.api import create_app

service = TenantService(repository, core_api_adapter)
app = create_app(service, authenticate=host_authenticator)
```

La aplicación expone OpenAPI en `/docs` y rutas versionadas bajo `/v1` para
perfiles, identificadores, contactos, domicilios, planes, precios,
prestaciones, contratos, suscripciones y facturación. `authenticate` debe ser
el mecanismo del host que valida el bearer/session token; los headers de
prueba no son un sustituto de autenticación en producción.

Permisos usados por el módulo incluyen `tenants:profile:read/write`,
`tenants:identifier:read/write`, `tenants:contact:read/write`,
`tenants:address:read/write`, `tenants:catalog:read/write`,
`tenants:contract:read/write`, `tenants:subscription:read/write` y
`tenants:billing:read/write`.

## Validación

```powershell
pytest -q tests_tenants
python -m compileall gi_common_tenants
```

Las pruebas unitarias usan memoria. Las pruebas PostgreSQL y las de Core real
se ejecutan sólo cuando el entorno de integración proporciona sus conexiones;
no se declaran aprobadas si la infraestructura no está disponible.
