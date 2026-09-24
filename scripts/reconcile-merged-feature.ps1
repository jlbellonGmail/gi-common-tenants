[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string] $Slug,
    [Parameter(Mandatory = $true)][int] $PrNumber,
    [Parameter(Mandatory = $true)][string] $Branch,
    [string] $BaseBranch = "develop",
    [string] $RepositoryRoot = ""
)

$ErrorActionPreference = "Stop"

function Invoke-GhJson([string[]] $Arguments) {
    $raw = & gh @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw "gh fallo: gh $($Arguments -join ' ')`n$($raw -join "`n")" }
    return (($raw | ForEach-Object { $_.ToString() }) -join "`n" | ConvertFrom-Json)
}

function Get-RoadmapState([string] $Content, [string] $Item) {
    $match = [regex]::Matches($Content, "(?m)^- \[(?<state>[ x-])\] $([regex]::Escape($Item))(?=\s|$).*$")
    if ($match.Count -ne 1) { throw "ROADMAP debe contener exactamente una entrada para '$Item'." }
    return $match[0].Groups["state"].Value
}

function Assert-Evidence([string] $Path, [string] $Pattern, [string] $Name) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Falta evidencia: $Path" }
    $text = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    if ($text -notmatch $Pattern) { throw "Evidencia inválida: $Name" }
    return $text
}

$root = if ($RepositoryRoot) { [IO.Path]::GetFullPath($RepositoryRoot) } else { (Get-Location).Path }
Push-Location $root
try {
    $pr = Invoke-GhJson @("pr", "view", $PrNumber, "--json", "number,state,baseRefName,headRefName,mergeCommit,statusCheckRollup")
    if ($pr.state -ne "MERGED") { throw "La PR #$PrNumber no está MERGED." }
    if ($pr.baseRefName -ne $BaseBranch) { throw "La PR #$PrNumber apunta a '$($pr.baseRefName)', no a '$BaseBranch'." }
    if ($pr.headRefName -ne $Branch) { throw "La PR #$PrNumber apunta a '$($pr.headRefName)', no a '$Branch'." }
    $mergeSha = [string]$pr.mergeCommit.oid
    if ([string]::IsNullOrWhiteSpace($mergeSha)) { throw "La PR #$PrNumber no tiene merge commit." }

    & git fetch origin $BaseBranch --prune *> $null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo actualizar origin/$BaseBranch." }
    & git merge-base --is-ancestor $mergeSha "origin/$BaseBranch" *> $null
    if ($LASTEXITCODE -ne 0) { throw "El merge commit $mergeSha no pertenece a origin/$BaseBranch." }

    $roadmapPath = Join-Path $root "ROADMAP.md"
    $roadmap = Get-Content -LiteralPath $roadmapPath -Raw -Encoding UTF8
    $state = Get-RoadmapState $roadmap $Slug
    $runDir = Join-Path $root (Join-Path "runs" $Slug)
    $authorization = Assert-Evidence (Join-Path $runDir "human-authorization.md") '(?m)^decision:\s*MERGE\s*$' "autorización humana"
    if ($authorization -notmatch "(?m)^scope:\s*$([regex]::Escape($Slug))\s*$") { throw "La autorización no corresponde al scope '$Slug'." }
    Assert-Evidence (Join-Path $runDir "independent-review.md") '(?m)^status:\s*approved\s*$' "revisión independiente" | Out-Null
    $integrity = Assert-Evidence (Join-Path $runDir "integrity-evidence.md") '(?im)\bPASS\b' "integridad"
    if ($integrity -match '(?im)\b(?:FAIL|ERROR|TIMEOUT)\b') { throw "La evidencia de integridad contiene un resultado negativo." }

    $requiredJobs = @("circuit-tests", "product-tests", "local-reconciler-tests")
    $checks = @($pr.statusCheckRollup | Where-Object { $_.workflowName -eq "CI" -and $_.name -in $requiredJobs })
    foreach ($job in $requiredJobs) {
        $check = $checks | Where-Object { $_.name -eq $job } | Select-Object -First 1
        if ($null -eq $check -or $check.conclusion -ne "SUCCESS") { throw "CI no verde para '$job'." }
    }

    if ($state -eq "x") {
        Write-Host "PASS: '$Slug' ya está cerrada; reconciliación idempotente sin cambios."
        exit 0
    }
    if ($state -notin @(' ', '-')) { throw "Estado ROADMAP no reconciliable para '$Slug': [$state]." }

    $updated = [regex]::Replace($roadmap, "(?m)^- \[$([regex]::Escape($state))\] ($([regex]::Escape($Slug))(?=\s|$).*)$", '- [x] $1', 1)
    Set-Content -LiteralPath $roadmapPath -Value $updated -Encoding UTF8
    & git add $roadmapPath
    if ($LASTEXITCODE -ne 0) { throw "No se pudo preparar ROADMAP.md." }
    & git commit -m "docs: reconciliar cierre post-merge $Slug"
    if ($LASTEXITCODE -ne 0) { throw "No se pudo registrar el cierre de '$Slug'." }
    & git push origin "HEAD:$BaseBranch"
    if ($LASTEXITCODE -ne 0) { throw "No se pudo publicar el cierre en origin/$BaseBranch." }
    Write-Host "PASS: '$Slug' reconciliada tras verificar PR #$PrNumber y merge $mergeSha."
}
finally { Pop-Location }
