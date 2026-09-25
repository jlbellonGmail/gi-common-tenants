# Conservación de evidencias HITL

El gate SingleMaintainer publica en la PR un bloque de evidencia con marcador estable, PR, scope, HEAD, base, decisión y resultados de CI, integridad y revisión. La reconciliación post-merge consulta los comentarios de la PR fusionada y valida todos esos campos antes de cerrar `ROADMAP.md`.

El archivo `human-authorization.md` continúa siendo válido cuando está versionado. El comentario de gate cubre el caso legítimo en que la autorización se registra después de estabilizar el HEAD y, por tanto, no puede agregarse a la rama sin invalidar la autorización.

No se acepta un comentario incompleto, de otra PR, otro scope, otro HEAD, otra base o sin resultados PASS. La operación sigue siendo idempotente y requiere merge real, revisión independiente, integridad y CI.
