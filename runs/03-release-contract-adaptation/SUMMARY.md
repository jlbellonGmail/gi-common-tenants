# 03-release-contract-adaptation

Estado: READY_FOR_PR
Versión: unreleased
Tipo: Feature
SDD: FULL
PR: pendiente
Merge: pendiente

## Objetivo

Adaptar el contrato de readiness de release para que un repositorio derivado
valide sus propias unidades de ROADMAP sin exigir fases históricas del
Template.

## Resultado

Se incorporó una política declarativa de release y un parser determinista de
unidades reales. Los gates de auditoría, integridad, CI, ramas y tags se
conservan.

## Cambios principales

- `release-policy.json` define la política del producto.
- `scripts/release-policy.ps1` centraliza el parsing y validaciones.
- `release-readiness.ps1` dejó de contener fases Template hardcodeadas.
- Se actualizaron documentación y pruebas de regresión.

## Validación

7 pruebas específicas PASS; adaptadores y supply chain PASS; `git diff --check`
PASS. Una unidad real abierta bloquea readiness y todas las unidades cerradas
sin fases Template pasan la validación de política.

## Decisiones

La política exige que todas las unidades reales del ROADMAP estén `[x]` y no
mantiene exclusiones por nombre. Los tags históricos son opcionales y sólo se
validan si la política los declara.

## Incidencias

La auditoría final de `v0.1.0` y el cierre de esta unidad requieren el circuito
normal de PR/HITL; no se crea tag ni release en esta unidad.

## Detalle

El parser ignora ejemplos dentro de fenced code blocks, rechaza estados `[ ]`
o `[-]`, exige al menos una unidad y mantiene la política read-only del
preflight.
