# Conservación de evidencias HITL

Estado: READY_FOR_PR
Versión: unreleased
Tipo: Feature de gobernanza
SDD: FULL
PR: pendiente de creación por el script oficial
Merge: pendiente

## Objetivo

Eliminar la incompatibilidad entre la evidencia local validada por SingleMaintainer y la evidencia exigida por el cierre post-merge.

## Resultado

El gate publica evidencia machine-readable en la PR y la reconciliación la valida por PR, scope, HEAD, base y controles PASS, conservando el fallback del archivo versionado.

## Cambios principales

- Publicación de comentario de evidencia antes del merge.
- Validación de comentarios de gate en la reconciliación.
- Regresiones contractuales.
- Documentación técnica y operativa.

## Validación

14 pruebas contractuales del gate y reconciliación pasan. La suite completa, CI remoto e integridad se ejecutarán antes de solicitar HITL.

## Decisiones

La autorización no se amplía ni se infiere: sólo se acepta evidencia con coincidencia exacta de PR, scope, HEAD y base. El archivo versionado sigue siendo una vía válida.

## Incidencias

La PR #8 demostró que el cierre podía fallar cuando el archivo local no llegaba a `develop`. La recuperación de esa unidad se ejecutará después de integrar esta corrección.

## Detalle

La implementación se limita a gobernanza y no modifica producto, Supabase, tags ni releases.
