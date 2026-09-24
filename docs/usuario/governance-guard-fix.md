# Operación del guard de develop

El workflow `Guard develop branch` clasifica los pushes a `develop` mediante el commit evaluado y las PR fusionadas hacia esa rama. Para consultar PR cerradas, el workflow obtiene JSON con `gh api` y aplica los filtros con `jq --arg`.

La regresión corregida se producía cuando una opción de `jq` se entregaba a `gh api`, que rechazaba la invocación antes de evaluar la autorización. La prueba contractual protege la separación entre ambos comandos.

La operación no requiere credenciales adicionales ni modifica ramas, tags, releases o datos del producto. Los merges autorizados por el circuito oficial siguen dependiendo de CI, revisión independiente, integridad y autorización HITL.
