# Decisión

Se mantiene `close-feature.ps1` para el flujo normal `[-] -> [x]`. La nueva
reconciliación cubre exclusivamente el caso recuperable de una PR ya MERGED
cuya unidad quedó `[ ]` o `[-]`, y nunca acepta una PR no fusionada.
