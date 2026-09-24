# Corrección del guard de develop

El fallback que verifica PR fusionadas consulta el listado de PR cerradas con
`gh api` y aplica el filtro con `jq --arg`. `--arg` no es una opción de
`gh api`; mantenerlo en esa invocación provoca que el CLI falle antes de
clasificar el push.

La corrección conserva los controles existentes: sólo reconoce PR fusionadas
contra `develop`, mantiene el rechazo de pushes no autorizados y no cambia la
remediación ni sus protecciones de concurrencia.
