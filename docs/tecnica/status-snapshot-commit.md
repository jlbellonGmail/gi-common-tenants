# Semántica del snapshot de STATUS

`update-status.ps1` captura el HEAD que describe antes de escribir `STATUS.md`.
Cuando el workflow post-merge commitea únicamente ese archivo, el commit nuevo
es un descendiente esperado del HEAD capturado.

`check-status.ps1` acepta ese caso sólo si todos los commits entre el HEAD del
snapshot y el HEAD actual modifican exclusivamente `STATUS.md`. Un commit
posterior que modifica funcionalidad, una rama distinta o un HEAD sin relación
ancestral sigue produciendo una advertencia o inconsistencia. La regla no usa
SHA hardcodeados y es idempotente para ejecuciones repetidas.
