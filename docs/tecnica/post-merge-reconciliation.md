# Reconciliación post-merge

`reconcile-merged-feature.ps1` cierra una unidad únicamente después de
verificar en GitHub que la PR está `MERGED`, apunta a `develop`, coincide con
la rama y el scope, y que su merge commit es ancestro del destino. También
exige autorización humana, revisión independiente, integridad y los tres jobs
CI aprobados.

El gate Post-HITL ejecuta la reconciliación en un checkout fresco de
`origin/develop`, por lo que el cierre no depende de que GitHub emita un evento
`pull_request_target.closed` después de un merge realizado con `GITHUB_TOKEN`.
El workflow post-merge conserva un dispatch manual para recuperar ejecuciones
históricas. La operación es idempotente si la unidad ya está en `[x]`.
