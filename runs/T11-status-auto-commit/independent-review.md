status: approved
scope: T11-status-auto-commit
head: d0d7b4301fcfce66e693d943e7b934fb1af3badf
base: develop
reviewer: independent-review
reviewedAt: 2026-09-25T05:00:00Z

# Revisión independiente

- `check-status.ps1` acepta sólo descendientes ancestrales cuyos commits
  intermedios modifican exclusivamente `STATUS.md`.
- Los commits funcionales posteriores, snapshots de otra rama y HEADs no
  ancestrales continúan siendo detectados.
- La regresión cubre snapshot exacto, commit automático, cambio funcional,
  snapshot real stale, rama distinta e idempotencia.

Veredicto: aprobado para preparar la PR, condicionado a que el HEAD y los
controles finales permanezcan vigentes.
