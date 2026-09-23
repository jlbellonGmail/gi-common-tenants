# Releases y evolución determinísticos

`scripts/release-readiness.ps1` es la ruta canónica y read-only para evaluar
un candidato SemVer. La política específica del repositorio vive en
`release-policy.json`: exige que todas las unidades reales de `ROADMAP.md`
estén cerradas y define la ubicación de la auditoría de release. No exige
fases históricas del repositorio Template.

El gate se ejecuta sobre `develop` limpio, comprueba que el commit local/remoto
coincide, que CI está verde sobre ese SHA, que la integridad pasa, que `main`
es ancestro (si existe), que el tag candidato no existe y que los tags
históricos declarados por la política, si los hubiera, permanecen inmutables.
`-DryRun` no crea PR, tag, release ni cambios remotos.

El flujo posterior es `develop` validado → PR contra `main` → gates → merge
humano → comprobación del commit final → tag anotado `vX.Y.Z` → release breve.
La primera release puede crear `main`; las siguientes sólo llegan por PR.
