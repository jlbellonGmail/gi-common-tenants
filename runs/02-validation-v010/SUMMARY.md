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
HEAD: b911635666a892e00160c626b987b6af2486c122
Base: develop
Estado: READY_FOR_HITL

## Evidencia

`check-integrity.ps1`: PASS.
`sync-agentic-adapters.ps1 -Check`: PASS.
`validate-supply-chain.ps1`: PASS.
`git diff --check`: PASS.
PostgreSQL 16, migraciones y RLS: PASS.
Integración Python y HTTP con Core v0.3.0: PASS.
CI: PASS en `circuit-tests`, `product-tests` y `local-reconciler-tests`.
