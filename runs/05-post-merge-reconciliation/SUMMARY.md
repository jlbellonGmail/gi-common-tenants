# 05-post-merge-reconciliation

Corrección general del cierre post-merge del Template. La unidad agrega una
reconciliación verificable e idempotente para PRs ya fusionadas y hace que el
gate SingleMaintainer invoque el cierre desde un checkout fresco de `develop`,
sin depender de eventos suprimidos por `GITHUB_TOKEN`.
