# Operación de reconciliación post-merge

El cierre normal se ejecuta automáticamente después del gate oficial. Para
recuperar una PR ya fusionada, un mantenedor autorizado puede ejecutar el
workflow `Post-merge feature close` con el slug, rama y número de PR reales.

El procedimiento valida el merge, la autorización, la revisión, la integridad
y CI antes de actualizar `ROADMAP.md`. No acepta PRs abiertas o cerradas sin
merge y no requiere credenciales personales.
