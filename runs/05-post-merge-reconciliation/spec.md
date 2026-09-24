# Especificación

La reconciliación sólo puede cerrar una unidad cuando la PR está MERGED contra
`develop`, su merge commit pertenece a la rama destino, el scope coincide,
autorización/revisión/integridad están aprobadas y los tres jobs CI están en
PASS. Las unidades abiertas, cerradas sin merge, scopes incorrectos, evidencias
negativas y CI incompleto deben fallar de forma segura. La operación es
idempotente cuando ROADMAP ya contiene `[x]`.
