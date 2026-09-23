# Releases y evolución

La política de release del producto está en `release-policy.json`. Para
validar una release ejecuta desde `develop` limpio:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\release-readiness.ps1 -Version v0.1.0 -DryRun
```

El resultado exitoso es sólo una validación: no publica nada. Si faltan
unidades reales cerradas, auditoría, CI, integridad, coherencia de ramas o el
tag ya existe, la operación se rechaza. La publicación requiere una PR
`develop` → `main`, merge humano, comprobación del SHA final, tag SemVer
inmutable y una release breve.
