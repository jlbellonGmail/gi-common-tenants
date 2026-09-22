# 02-validation-v010

## Objetivo

Validar PostgreSQL/Core del módulo GI-COMMON-TENANTS y preparar v0.1.0 sin
crear tag ni publicar release.

## Resultado

La migración se ejecutó desde una base vacía y repetidamente en PostgreSQL 16.
RLS filtró registros por `app.tenant_id` y las claves compuestas rechazaron
referencias cruzadas entre tenant, contrato y plan/precio. Core v0.3.0 fue
validado mediante su biblioteca Python y su HTTP de identidad publicado.
Creación/listado/autorización no tienen contrato HTTP publicado y permanecen
fail-closed.

PR: #2
HEAD: db2313db0c6b30cda63d9616011dc4fc7a6d801f
Estado: READY_FOR_HITL
