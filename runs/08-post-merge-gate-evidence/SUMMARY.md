# Compatibilidad de evidencia post-merge

Estado: READY_FOR_PR
Versión: unreleased
Tipo: Feature de gobernanza
SDD: FULL
PR: pendiente de creación por el script oficial
Merge: pendiente

## Objetivo

Completar la aceptación de evidencia durable para revisión e integridad en el cierre post-merge.

## Resultado

La reconciliación acepta el gate de PR completo y sólo exige archivos locales cuando ese gate no existe.

## Cambios principales

- Ajuste condicional de la reconciliación.
- Regresión contractual.
- Documentación operativa.

## Validación

La prueba contractual específica pasa; CI e integridad remotos se ejecutarán sobre el HEAD definitivo.

## Decisiones

No se relajan controles: el comentario debe coincidir con PR, scope, HEAD, base, decisión y resultados PASS.

## Incidencias

La PR #9 mostró que la revisión e integridad también podían faltar del checkout confiable aunque el gate las hubiera validado.

## Detalle

Corrección limitada al circuito de gobernanza; no modifica producto, Supabase, tags ni releases.
