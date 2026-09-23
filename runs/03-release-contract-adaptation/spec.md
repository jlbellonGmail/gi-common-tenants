# Especificación

## Problema

El preflight exigía cinco unidades históricas del repositorio Template que no
forman parte del ROADMAP de GI-COMMON-TENANTS.

## Contrato

La política versionada en `release-policy.json` exige que todas las unidades
de producto presentes en `ROADMAP.md` estén cerradas. El preflight no conoce
identidades Template. Las auditorías obligatorias, CI, integridad, coherencia
de ramas, tags candidatos y autorizaciones de los circuitos existentes siguen
siendo obligatorias.

## No objetivos

No publicar releases, crear tags, modificar AGENTS.md ni alterar otros
repositorios.
