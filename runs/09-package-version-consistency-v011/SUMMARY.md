Estado: READY_FOR_PR
Versión: 0.1.1
Tipo: Feature
SDD: FULL
PR: pendiente de creación por el gate
Merge: no realizado

## Objetivo

Corregir la versión pública de Tenants para que coincida con sus metadatos.

## Resultado

`gi_common_tenants.__version__` ahora expone `0.1.1`.

## Cambios principales

Se actualizó el módulo, se agregó prueba de coherencia, documentación y
artefacto wheel reproducible.

## Validación

12 tests pasaron y uno se omitió por ausencia de PostgreSQL real.

## Decisiones

El tag/release existente no se modificó; cualquier nueva publicación queda
sujeta a la decisión de release correspondiente.

## Incidencias

El wheel publicado `v0.1.1` conserva el módulo `0.1.0`, aunque su metadata es
`0.1.1`.

## Detalle

La evidencia está en `validation-evidence.md`. No hubo merge ni nueva release.
