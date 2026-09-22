# Preparación de GI-COMMON-TENANTS v0.1.0

La versión `v0.1.0` está preparada como candidata, pero no publicada. La
publicación requiere autorización HITL sobre una PR de release hacia `main`,
un tag anotado sobre el commit aprobado y una release GitHub.

Validaciones de la candidata:

- PostgreSQL 16: migración desde base vacía, ejecución repetida, RLS y FKs compuestas.
- Core v0.3.0: contratos Python y superficie HTTP de identidad publicada.
- CI: suite de circuito, producto/PostgreSQL y reconciliador Windows.

Core no publica todavía por HTTP la creación/listado de tenants ni la
autorización; esas operaciones deben consumirse mediante la biblioteca Python.
