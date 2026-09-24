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

## Validación

La suite local del circuito y de producto se ejecuta antes de solicitar CI;
las evidencias remotas quedan vinculadas al HEAD definitivo de la PR.

## Evidencias

`spec.md`, `plan.md`, `tasks.md`, `decision.md`, `audit-1.md`,
`test-report-1.md`, `code-review-1.md` e `integrity-evidence.md`.

## Resultado

La implementación local y las regresiones determinísticas pasan. La validación
remota de CI y el único gate HITL se ejecutarán sobre el HEAD publicado de la
PR.

## Cambios principales

- Nuevo reconciliador post-merge con validaciones de PR, merge, evidencias y CI.
- Invocación desde el gate SingleMaintainer en checkout aislado.
- Dispatch manual para recuperación de cierres históricos.
- Regresiones de contrato y documentación operativa.

## Decisiones

Se conserva el gate humano y la política de mínimo privilegio. La reconciliación
no sustituye autorización ni merge: sólo verifica un merge ya confirmado y
actualiza el estado documental de forma idempotente.

## Incidencias

La incidencia que originó esta unidad fue la supresión del evento de cierre
posterior a un merge realizado con `GITHUB_TOKEN`; queda cubierta por el cierre
explícito del gate y el dispatch de recuperación.

## Detalle

La validación del merge consulta GitHub en vivo y comprueba la relación entre
PR, rama, scope, commit destino y evidencias antes de escribir `ROADMAP.md`.

Estado: READY_FOR_PR
Versión: unreleased
PR: pendiente de creación por el script oficial
Merge: pendiente
