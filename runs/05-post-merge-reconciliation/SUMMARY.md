# 05-post-merge-reconciliation

Corrección general del cierre post-merge del Template. La unidad agrega una
reconciliación verificable e idempotente para PRs ya fusionadas y hace que el
gate SingleMaintainer invoque el cierre desde un checkout fresco de `develop`,
sin depender de eventos suprimidos por `GITHUB_TOKEN`.

## Objetivo

Cerrar de forma segura una unidad cuya PR ya fue fusionada y evitar que el
cierre dependa exclusivamente de `pull_request_target.closed`.

## Alcance

Scripts de gobernanza, workflows post-merge, evidencias y pruebas de contrato.
No modifica el dominio de tenants, Core ni Supabase.

## Criterios de aceptación

- PR no fusionada, base incorrecta, rama incorrecta, merge commit no alcanzable,
  evidencias ausentes o CI incompleto deben fallar.
- PR fusionada válida puede pasar `[ ]` o `[-]` a `[x]` una sola vez.
- Una unidad `[x]` se reconcilia sin cambios.
- El gate Post-HITL invoca el cierre sin depender del evento suprimido.

## Riesgos y mitigaciones

El cierre publica sólo en `develop` después de consultar GitHub y validar
evidencias; no usa PAT ni force-push. La operación es idempotente y fail-safe.

## Validaciones

Tests de contrato, suite del circuito, tests de producto, sintaxis PowerShell,
adaptadores agentic, supply chain y diff limpio.

## Evidencias

`spec.md`, `plan.md`, `tasks.md`, `decision.md`, `audit-1.md`,
`test-report-1.md`, `code-review-1.md` e `integrity-evidence.md`.
