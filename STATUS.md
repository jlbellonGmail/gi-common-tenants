# Estado operativo

GI-COMMON-TENANTS está en implementación inicial sobre el Template instalado.
La rama de trabajo contiene el dominio, la persistencia PostgreSQL, las
superficies Python/HTTP, la integración Python con Core v0.3.0 y pruebas
unitarias/integración local. La validación contra PostgreSQL real y la API HTTP
remota de Core quedan condicionadas a que el entorno proporcione esos servicios.

## Próximo paso

Ejecutar la migración en una base de desarrollo autorizada, probar RLS y
verificar la integración HTTP cuando Core publique las capacidades faltantes.
Luego preparar PR y revisión HITL; no hacer merge ni release automáticamente.

<!-- STATUS:AUTO:BEGIN -->

## Estado verificado automáticamente

- Actualizado: 2026-09-22T13:21:10Z
- Versión: unreleased
- Rama: feature/01-tenants-implementation
- HEAD: ce59b2c35b0b3ef89df21861b7bc27591d85a4ed
- Remoto: https://github.com/jlbellonGmail/gi-common-tenants.git
- Working tree: dirty
- Worktrees: 3
- Worktrees Git: 3
- Unidades activas: = [feature/01-tenants-implementation]
- PR activa: UNKNOWN / sin PR abierta
- CI: UNKNOWN / sin CI verificable
- CI vigente: UNKNOWN / sin CI verificable
- Última release: UNKNOWN / no disponible

<!-- STATUS:AUTO:END -->
