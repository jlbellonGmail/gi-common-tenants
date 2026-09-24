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

- Actualizado: 2026-09-24T15:59:08Z
- Versión: unreleased
- Rama: develop
- HEAD: 80b396b8f40e403db337626499f6b868e209e6cb
- Remoto: https://github.com/jlbellonGmail/gi-common-tenants
- Working tree: dirty
- Worktrees: 3
- Worktrees Git: 3
- Unidades activas: ninguna
- PR activa: UNKNOWN / sin PR abierta
- CI:  @ ba38f5d329d8a18ccea0be171ca79671bbafd0f4
- CI vigente:  @ ba38f5d329d8a18ccea0be171ca79671bbafd0f4
- Última release: v0.1.1

<!-- STATUS:AUTO:END -->
