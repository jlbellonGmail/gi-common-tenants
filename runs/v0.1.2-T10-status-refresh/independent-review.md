status: approved
scope: T10-status-refresh
head: HEAD
base: develop
reviewer: independent-review
reviewedAt: 2026-09-25T03:00:00Z

# Revisión independiente

- `update-status.ps1` es el único mecanismo usado para regenerar el bloque
  automático de `STATUS.md`.
- El workflow post-merge omite `reconcile-merged-feature.ps1` sólo para
  maintenance auxiliar y conserva la sincronización de STATUS en `develop`.
- La regresión contractual cubre ambas condiciones y no modifica producto,
  Supabase, tags, releases ni artefactos.

Veredicto: aprobado para PR contra `develop`.
