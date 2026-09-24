status: approved
attempt: 1
scope: 05-post-merge-reconciliation
head: 8c937acf3a5fe346081a25e9b3685bd4abd18d00
base: develop
feedback:
  - "PASS: la reconciliación valida PR MERGED, base develop, rama esperada y merge commit alcanzable desde develop."
  - "PASS: la operación requiere autorización humana, revisión independiente, integridad y los tres checks CI."
  - "PASS: los estados pendiente, READY_FOR_PR y completado se procesan de forma fail-safe e idempotente."
  - "PASS: las pruebas de contrato cubren rechazo de PR no fusionada, evidencias inválidas y cierre repetido."
  - "PASS: el cambio no modifica otros repositorios, no usa PAT y no altera datos externos."
