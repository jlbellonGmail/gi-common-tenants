# Evidencia completa del cierre post-merge

Cuando existe un bloque `GI-SINGLEMAINTAINER-GATE` válido en los comentarios de la PR, la reconciliación usa sus campos exactos de identidad y sus resultados PASS como evidencia durable de autorización, revisión e integridad. Sólo usa los archivos locales como fallback cuando no existe ese bloque.
