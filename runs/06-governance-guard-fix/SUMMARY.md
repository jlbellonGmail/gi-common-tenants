# Corrección del guard de develop

Estado: READY_FOR_PR
Versión: unreleased
Tipo: Feature de gobernanza
SDD: FULL
PR: pendiente de creación por el script oficial
Merge: pendiente

## Objetivo

Corregir el fallback de consulta de PR cerradas del workflow `guard-develop-branch.yml` y verificar el circuito de gobernanza sin modificar el producto, Supabase, tags ni releases.

## Resultado

La causa raíz del run `35969238489` fue reproducida y corregida: `--arg` se pasaba a `gh api` en lugar de a `jq`. La corrección queda lista para revisión, CI y autorización HITL.

## Cambios principales

- El fallback canaliza la respuesta JSON de `gh api` a `jq --arg`.
- Se conserva el filtro de PR fusionada hacia `develop`.
- Se añade una regresión contractual del workflow.
- Se documentan diagnóstico, decisión y evidencias de gobernanza.

## Validación

31 pruebas contractuales pasaron; `sync-agentic-adapters.ps1 -Check` y `validate-supply-chain.ps1` pasaron. La validación remota queda pendiente de la PR.

## Decisiones

Se conserva el gate humano, la política de mínimo privilegio y la clasificación fail-safe. La corrección no introduce credenciales, excepciones históricas ni cambios al producto.

## Incidencias

El run histórico falló con `accepts 1 arg(s), received 4` porque `gh api` recibió opciones propias de `jq`. No hay otra incidencia técnica conocida en el alcance de esta unidad.

## Detalle

La evidencia primaria está en `runs/06-governance-guard-fix/`, incluyendo `assess.jsonl`, `sdd.json`, especificación, plan, tareas, decisión, auditoría, QA, code review, revisión independiente e integridad.
