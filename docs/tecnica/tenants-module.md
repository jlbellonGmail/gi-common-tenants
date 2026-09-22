# Arquitectura de GI-COMMON-TENANTS

## Propiedad y dependencias

El agregado técnico `Tenant` y su `tenant_id` pertenecen exclusivamente a
GI-PLATFORM-CORE. Este repositorio guarda el perfil administrativo y las
relaciones comerciales que referencian ese identificador opaco. No existe
`tenants.tenants` ni una FK contra `core.tenants`.

La capa de aplicación depende de puertos: `CoreApiAdapter` consume la
biblioteca Python pública de Core v0.3.0 y `HttpCoreAdapter` consume sólo la
especificación HTTP publicada. La persistencia se intercambia entre
`InMemoryTenantRepository` y `PostgresTenantRepository` sin modificar las
reglas del servicio.

## Persistencia

La migración inicial crea diez tablas funcionales y `audit_events` en el
schema `tenants`. Catálogos son globales; los demás registros llevan
`tenant_id`. Los precios se copian a `price_snapshot` al crear una
suscripción, para que una modificación futura del catálogo no altere las
condiciones contratadas.

Las operaciones críticas usan transacción, índices únicos y control
optimista por `version`. PostgreSQL además aplica RLS y la aplicación establece
el contexto `app.tenant_id` por conexión/transacción en el adaptador.

## Autorización

Ningún `tenant_id` enviado por el consumidor se considera prueba de permiso.
El servicio exige que coincida con el contexto autenticado y delega cada
permiso en Core. Las capacidades no publicadas por Core se rechazan con
`CAPABILITY_UNAVAILABLE` o `CORE_UNAVAILABLE`; no hay fallback administrativo.

## Estados comerciales

El estado técnico de Core, el estado del contrato, el estado de la
suscripción y el estado del plan son independientes. Cancelar o vencer una
suscripción no elimina el tenant ni cambia tablas de Core.
