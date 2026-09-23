# Uso del contrato de release

Ejecutar desde `develop` limpio:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\release-readiness.ps1 -Version v0.1.0 -DryRun
```

El resultado es sólo una validación. Una unidad real pendiente o una
auditoría de release ausente bloquea la operación. El comando no crea tags,
releases ni publica artefactos.
