# Adaptación del contrato de release

Esta unidad adapta el preflight del Template a un repositorio derivado. La
fuente de unidades exigibles es `ROADMAP.md`; el contrato exige que todas las
unidades reales estén cerradas. La política se encuentra en
`release-policy.json` y se valida mediante `scripts/release-policy.ps1`.

Las fases históricas del Template no se copian al ROADMAP del producto. La
adaptación conserva las verificaciones de auditoría de release, integridad,
CI, coherencia de ramas, tags candidatos y tags históricos declarados.
