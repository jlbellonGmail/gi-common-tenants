status: approved
attempt: 1
scope: 03-release-contract-adaptation
head: HEAD
base: develop
feedback:
  - PASS: el preflight obtiene la política declarativa del repositorio y no contiene las fases históricas 18–22 del Template.
  - PASS: todas las unidades reales del ROADMAP deben estar cerradas; una unidad pendiente o READY_FOR_PR bloquea la release.
  - PASS: permanecen activos los checks de auditoría, integridad, CI, ramas, tags y el carácter read-only del preflight.
  - PASS: las regresiones cubren roadmap fenced, unidades abiertas, unidades cerradas y conservación de gates.
