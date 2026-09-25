# Consistencia del paquete v0.1.1

La fuente corregida expone `gi_common_tenants.__version__ == "0.1.1"`,
coherente con `pyproject.toml`. El tag y release `v0.1.1` existentes son
inmutables y su wheel publicado fue construido antes de esta corrección;
por eso esta unidad deja la corrección en PR y no sobrescribe el asset.

La verificación reproducible construye un wheel desde el commit de la PR y
comprueba los metadatos de distribución, el import público y las APIs
`TenantContext`, `TenantService`, `TenantsApi` y `TenantsError`.
