function Get-ReleasePolicy {
    param([Parameter(Mandatory = $true)][string] $RepositoryRoot)

    $path = Join-Path $RepositoryRoot "release-policy.json"
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Falta la politica declarativa de release: $path"
    }

    try { $policy = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json }
    catch { throw "Politica declarativa de release invalida: $path" }

    if ($policy.schemaVersion -ne 1) { throw "Politica declarativa de release incompatible: schemaVersion." }
    if ($null -eq $policy.roadmap -or $policy.roadmap.requireAllUnitsClosed -ne $true) {
        throw "Politica declarativa de release invalida: roadmap.requireAllUnitsClosed debe ser true."
    }
    if ($null -eq $policy.releaseAudit -or [string]::IsNullOrWhiteSpace([string]$policy.releaseAudit.directory)) {
        throw "Politica declarativa de release invalida: falta releaseAudit.directory."
    }

    $files = @($policy.releaseAudit.files | ForEach-Object { [string]$_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($files.Count -eq 0) { throw "Politica declarativa de release invalida: releaseAudit.files esta vacio." }
    return $policy
}

function Get-ReleaseRoadmapUnits {
    param([Parameter(Mandatory = $true)][string] $Content)

    $fenced = $false
    $units = @()
    foreach ($line in ($Content -split "`r?`n")) {
        if ($line.TrimStart().StartsWith('```')) { $fenced = -not $fenced; continue }
        if ($fenced) { continue }
        $match = [regex]::Match($line, '^(?:- )\[(?<state>[ x-])\] (?<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\b')
        if ($match.Success) {
            $units += [pscustomobject]@{
                Slug = $match.Groups['slug'].Value
                State = $match.Groups['state'].Value
            }
        }
    }
    return $units
}

function Assert-ReleaseRoadmapComplete {
    param([Parameter(Mandatory = $true)][object[]] $Units)

    if ($Units.Count -eq 0) { throw "ROADMAP sin unidades de producto; se rechaza la release." }
    $open = @($Units | Where-Object { $_.State -ne 'x' })
    if ($open.Count -gt 0) {
        $details = ($open | ForEach-Object { "$($_.Slug) [$($_.State)]" }) -join ', '
        throw "ROADMAP incompleto: unidades reales no cerradas: $details."
    }
}

function Resolve-ReleaseAuditPath {
    param(
        [Parameter(Mandatory = $true)][string] $RepositoryRoot,
        [Parameter(Mandatory = $true)][string] $Version,
        [Parameter(Mandatory = $true)] $Policy
    )
    $relative = ([string]$Policy.releaseAudit.directory).Replace('{version}', $Version)
    return Join-Path $RepositoryRoot $relative
}

function Assert-ImmutableReleaseTags {
    param([Parameter(Mandatory = $true)] $Policy)

    foreach ($entry in @($Policy.immutableTags)) {
        $name = [string]$entry.name
        $commit = [string]$entry.commit
        if ([string]::IsNullOrWhiteSpace($name) -or [string]::IsNullOrWhiteSpace($commit)) {
            throw "Politica declarativa invalida: immutableTags requiere name y commit."
        }
        $actual = & git rev-parse "$name^{commit}" 2>$null
        if ($LASTEXITCODE -ne 0 -or (($actual | Out-String).Trim() -ne $commit)) {
            throw "Tag historico inmutable '$name' no coincide con el commit declarado."
        }
        $type = (& git cat-file -t $name 2>$null | Out-String).Trim()
        if ($type -ne 'tag') { throw "Tag historico inmutable '$name' debe ser anotado." }
    }
}
