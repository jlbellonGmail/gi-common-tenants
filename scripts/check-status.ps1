param([switch]$Json)

$ErrorActionPreference = "Stop"

function Invoke-Git([string[]]$Arguments) {
    $output = & git @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw "git command failed: git $($Arguments -join ' ')" }
    return (($output | ForEach-Object { $_.ToString() }) -join "`n").Trim()
}

function Get-StatusField([string]$Block, [string]$Name) {
    $match = [regex]::Match($Block, "(?m)^- $([regex]::Escape($Name)): (.*)$")
    if (-not $match.Success) { throw "Falta el campo $Name" }
    return $match.Groups[1].Value.Trim()
}

function Invoke-Optional([string]$File, [string[]]$Arguments) {
    if (-not $File) { return [pscustomobject]@{ Code = 127; Text = "" } }
    $output = & $File @Arguments 2>&1
    return [pscustomobject]@{ Code = $LASTEXITCODE; Text = (($output | ForEach-Object { $_.ToString() }) -join "`n").Trim() }
}

function Test-StatusOnlyDescendant([string]$SnapshotHead, [string]$CurrentHead) {
    if ($SnapshotHead -eq $CurrentHead) { return $true }
    & git merge-base --is-ancestor $SnapshotHead $CurrentHead 2>$null
    if ($LASTEXITCODE -ne 0) { return $false }
    $commitText = Invoke-Git @("rev-list", "--reverse", "$SnapshotHead..$CurrentHead")
    $commits = @($commitText -split "`r?`n" | Where-Object { $_ })
    if ($commits.Count -eq 0) { return $false }
    foreach ($commit in $commits) {
        $pathText = Invoke-Git @("diff-tree", "--no-commit-id", "--name-only", "-r", $commit)
        $paths = @($pathText -split "`r?`n" | Where-Object { $_ })
        if ($paths.Count -eq 0 -or @($paths | Where-Object { $_ -ne "STATUS.md" }).Count -gt 0) { return $false }
    }
    return $true
}

try {
    $root = Invoke-Git @("rev-parse", "--show-toplevel")
    $statusPath = Join-Path $root "STATUS.md"
    if (-not (Test-Path -LiteralPath $statusPath -PathType Leaf)) { Write-Host "ERROR ERROR_REAL No existe STATUS.md"; exit 1 }
    $content = Get-Content -Raw -Encoding UTF8 $statusPath
    $begin = ([regex]::Matches($content, [regex]::Escape("<!-- STATUS:AUTO:BEGIN -->"))).Count
    $end = ([regex]::Matches($content, [regex]::Escape("<!-- STATUS:AUTO:END -->"))).Count
    if ($begin -ne 1 -or $end -ne 1) { Write-Host "ERROR INCONSISTENTE marcadores AUTO invalidos"; exit 1 }
    $block = ([regex]::Match($content, '(?s)<!-- STATUS:AUTO:BEGIN -->.*?<!-- STATUS:AUTO:END -->')).Value
    $branch = Invoke-Git @("branch", "--show-current"); if (-not $branch) { $branch = "(detached)" }
    $head = Invoke-Git @("rev-parse", "HEAD")
    $errors = @(); $warnings = @()
    if ((Get-StatusField $block "Rama") -ne $branch) { $errors += "INCONSISTENTE rama no coincide" }
    $snapshotHead = Get-StatusField $block "HEAD"
    if (-not (Test-StatusOnlyDescendant $snapshotHead $head)) { $warnings += "STALE HEAD: snapshot regenerable" }
    $tree = if ((Invoke-Git @("status", "--porcelain"))) { "dirty" } else { "clean" }
    if ((Get-StatusField $block "Working tree") -ne $tree) { $warnings += "STALE working tree: snapshot regenerable" }
    $gh = (Get-Command gh -ErrorAction SilentlyContinue).Source
    if (-not $gh) { $warnings += "TEMPORAL gh no disponible; PR/CI no verificables" }
    else {
        $pr = Invoke-Optional $gh @("pr", "list", "--head", $branch, "--state", "open", "--json", "number,headRefOid", "--limit", "1")
        if ($pr.Code -ne 0) { $warnings += "TEMPORAL PR no verificable" }
        elseif ($pr.Text -and $pr.Text -ne "[]") { $activePr = $pr.Text | ConvertFrom-Json; if ((Get-StatusField $block "PR activa") -notmatch [regex]::Escape([string]$activePr[0].number)) { $warnings += "STALE PR: snapshot regenerable" } }
        $ci = Invoke-Optional $gh @("run", "list", "--branch", $branch, "--limit", "1", "--json", "headSha,status,conclusion")
        if ($ci.Code -ne 0) { $warnings += "TEMPORAL CI no verificable" }
        elseif ($ci.Text -and $ci.Text -ne "[]") { $latestCi = ($ci.Text | ConvertFrom-Json)[0]; if ((Get-StatusField $block "CI") -notmatch [regex]::Escape([string]$latestCi.headSha)) { $warnings += "STALE CI: HEAD regenerable" } }
    }
    if ($Json) { [ordered]@{ status = if ($errors.Count) { "INCONSISTENTE" } elseif ($warnings.Count) { "STALE" } else { "OK" }; errors = $errors; warnings = $warnings; branch = $branch; head = $head } | ConvertTo-Json -Depth 5; exit 0 }
    $errors | ForEach-Object { Write-Host "ERROR $_" }; $warnings | ForEach-Object { Write-Host "WARNING $_" }
    if ($errors.Count) { exit 1 }; Write-Host "PASS STATUS.md coherente"; exit 0
}
catch { Write-Host ("ERROR ERROR_REAL " + $_.Exception.Message); exit 2 }
