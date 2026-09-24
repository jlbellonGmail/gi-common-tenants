# Estado operativo

GI-COMMON-TENANTS está validado en una rama de trabajo sobre el Template
instalado. La rama contiene el dominio, persistencia PostgreSQL, superficies
Python/HTTP, integración Python con Core v0.3.0, HTTP de identidad y pruebas
reales de PostgreSQL/RLS.

La migración se ejecutó desde una base vacía y repetidamente en PostgreSQL 16.
La integración HTTP remota de Core queda limitada a identidad: Core v0.3.0 no
publica por HTTP creación, listado ni autorización. Esas capacidades quedan
verificadas mediante la biblioteca Python y fallan cerrado por HTTP.

## Próximo paso

Revisar la PR de validación y ejecutar HITL. La candidata v0.1.0 está
preparada, pero no se debe crear tag ni publicar release automáticamente.

<!-- STATUS:AUTO:BEGIN -->

## Estado verificado automáticamente

- Actualizado: 2026-09-24T03:49:06Z
- Versión: unreleased
- Rama: feature/04-tenants-permissions
- HEAD: d3be99d1ed4a39a23b6aedbd2ce8669f4852b27b
- Remoto: https://github.com/jlbellonGmail/gi-common-tenants.git
- Working tree: dirty
- Worktrees: 3
- Worktrees Git: 3
- Unidades activas: = [feature/03-release-contract-adaptation]; = [feature/04-tenants-permissions]
- PR activa: UNKNOWN / sin PR abierta
- CI: UNKNOWN / sin CI verificable
- CI vigente: UNKNOWN / sin CI verificable
- Última release: UNKNOWN / no disponible

<!-- STATUS:AUTO:END -->
