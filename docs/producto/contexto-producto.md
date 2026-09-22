# Contexto de producto — GI-COMMON-TENANTS

GI-COMMON-TENANTS administra la relación comercial entre GI y los clientes
que contratan la plataforma. Conserva perfiles administrativos, identificadores
legales/fiscales, contactos, domicilios, catálogo de planes, precios,
prestaciones, contratos, suscripciones y configuración de facturación.

## Límites

GI-PLATFORM-CORE es propietario de la identidad técnica, `tenant_id`, ciclo
de vida técnico, autenticación, usuarios, membresías, roles, permisos, sedes
y aislamiento. Common-Tenants consume sus contratos públicos y no accede a sus
tablas privadas. GI-COMMON-PERSONS administra personas de negocio y no es un
requisito para el titular administrativo del tenant.

Este módulo no emite comprobantes, procesa pagos, administra contabilidad,
CRM ni personas de negocio verticales.

## Estado comercial

Los estados de Core, contrato, suscripción y plan son independientes. Una
cancelación comercial conserva el historial y no elimina la identidad técnica.
Los precios y prestaciones contratados se guardan como snapshot en la
suscripción para impedir cambios retroactivos.
