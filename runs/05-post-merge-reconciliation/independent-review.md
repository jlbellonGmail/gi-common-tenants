status: approved
attempt: 1
scope: 05-post-merge-reconciliation
head: f93d782604e57107b7c48b955856def1b5fa62c0
base: develop
feedback:
  - "PASS: la reconciliación valida PR MERGED, base develop, rama esperada y merge commit alcanzable desde develop."
  - "PASS: la operación requiere autorización humana, revisión independiente, integridad y los tres checks CI."
  - "PASS: los estados pendiente, READY_FOR_PR y completado se procesan de forma fail-safe e idempotente."
  - "PASS: las pruebas de contrato cubren rechazo de PR no fusionada, evidencias inválidas y cierre repetido."
  - "PASS: el cambio no modifica otros repositorios, no usa PAT y no altera datos externos."
