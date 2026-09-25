Estado: READY_FOR_PR
Versión: 0.1.2
Tipo: Feature
SDD: FULL
PR: pendiente de creación
Merge: no realizado

## Objetivo

Preparar la versión correctiva `0.1.2` con metadata, módulo, wheel,
documentación y verificaciones coherentes, sin sobrescribir `v0.1.1`.

## Resultado

`pyproject.toml`, `gi_common_tenants.__version__` y el wheel reproducible
reportan `0.1.2`.

## Cambios principales

Se actualizaron metadata, módulo, prueba de coherencia, documentación e
índices. Se conservó un wheel reproducible en la evidencia de la unidad.

## Validación

La suite Tenants en entorno virtual limpio pasó `12 passed, 1 skipped`; CI
debe confirmar la suite completa y PostgreSQL/RLS antes del merge.

## Decisiones

La release/tag `v0.1.1` permanece inmutable. No se crea tag ni release desde
esta unidad.

## Incidencias

La suite completa local quedó detenida en una prueba de sincronización de
adaptadores en este host; se conserva como incidencia y queda exigida por CI.

## Detalle

La evidencia completa está en `validation-evidence.md`; la PR se crea contra
`develop` y no se mergea automáticamente.
