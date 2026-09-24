# Especificación

Corregir la versión pública de `gi_common_tenants` para que el módulo exponga
`__version__ == 0.1.1`, igual que `pyproject.toml`, sin reescribir el tag o
release ya publicados. Verificar APIs públicas, construir un wheel reproducible
desde la rama y documentar que el asset `v0.1.1` existente requiere una nueva
decisión de release para reemplazarse.

Fuera de alcance: Core, Persons, tags, releases y merges.
