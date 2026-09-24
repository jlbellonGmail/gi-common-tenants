# Corrección del guard de develop

Esta unidad corrige el fallback de consulta de PR cerradas del workflow
`guard-develop-branch.yml`. El fallo histórico se reprodujo en el run
`35969238489`, cuyo log registró `accepts 1 arg(s), received 4` al pasar
`--arg` a `gh api`.

La corrección canaliza la respuesta JSON a `jq --arg`, conserva el alcance
`develop` y no modifica el producto, Supabase, tags ni releases.
