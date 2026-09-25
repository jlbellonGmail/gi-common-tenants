# ROADMAP

## Cómo usar este archivo

Este mapa registra las unidades del proyecto nuevo. `[ ]` significa
pendiente, `[-]` significa `READY_FOR_PR` y `[x]` significa mergeada y
cerrada. Una unidad solo pasa a `[x]` después del merge a `develop` y del
cierre post-merge automático.

## Backlog

Agregá aquí cada feature o milestone con una identidad única, por ejemplo:

```text
- [ ] 01-mi-feature — Descripción funcional breve y verificable.
```

No registres aquí fases históricas del template ni evidencias de ejecución.

- [x] 01-tenants-implementation — Implementar administración administrativa, comercial, contractual y de suscripciones con Core v0.3.0.
- [x] 02-validation-v010 — Validar PostgreSQL/Core, corregir hallazgos y preparar v0.1.0 para HITL sin publicar.
- [x] 03-release-contract-adaptation — Adaptar el preflight de release para validar las unidades reales del producto derivado.
- [x] 04-tenants-permissions — Aplicar privilegios mínimos y validar acceso RLS en Supabase gi-dev.
- [x] 05-post-merge-reconciliation — Corregir y reconciliar el cierre post-merge del Template sin depender de eventos suprimidos por GITHUB_TOKEN.
- [x] 06-governance-guard-fix — Corregir la detección del guard de develop y verificar el circuito de gobernanza sin alterar el producto.
- [x] 08-post-merge-gate-evidence — Completar la compatibilidad de evidencia del cierre post-merge.
- [x] 09-package-version-consistency-v011 — Corregir la versión pública del módulo para que el artefacto de Tenants 0.1.1 sea coherente con sus metadatos, verificaciones y documentación.
- [ ] 10-package-version-consistency-v012 — Preparar la versión correctiva 0.1.2 con metadatos, módulo, wheel, documentación y controles coherentes.

## Fuentes de orientación

- [CONSTITUTION](CONSTITUTION.md) — principios permanentes.
- [AGENTS](AGENTS.md) — operación del circuito.
- [STATUS](STATUS.md) — estado actual para reentrada.

































- [x] 07-governance-evidence-preservation — Conservar evidencias HITL compatibles entre el gate de merge y el cierre post-merge.







