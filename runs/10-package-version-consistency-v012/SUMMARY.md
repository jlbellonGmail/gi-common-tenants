Estado: READY_FOR_PR
Versión: 0.1.2
Tipo: Feature
SDD: FULL
PR: #12 abierta contra `develop`
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

La suite Tenants en entorno virtual limpio pasó `12 passed, 1 skipped`.
El CI final de la PR #12 pasa los tres jobs obligatorios.

## Decisiones

La release/tag `v0.1.1` permanece inmutable. No se crea tag ni release desde
esta unidad; la publicación futura requiere decisión humana.

## Incidencias

La suite completa local quedó detenida en una prueba de sincronización de
adaptadores en este host; CI remoto sí la verificó correctamente.

## Detalle

La evidencia completa está en `validation-evidence.md`; la PR #12 queda
abierta contra `develop` y no se mergea automáticamente.
