# Evidencia de cierre post-merge

Al completar un merge autorizado, el gate publica un comentario auditable en la PR. Ese comentario permite que el cierre posterior verifique la autorización y los controles aunque el archivo local de autorización no haya formado parte del HEAD fusionado.

La reconciliación sólo cierra unidades con PR fusionada, base y rama correctas, HEAD coincidente, revisión independiente aprobada, integridad PASS y CI verde.
