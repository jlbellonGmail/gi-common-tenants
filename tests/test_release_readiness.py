import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "release-readiness.ps1"


def run(*args):
    return subprocess.run(
        ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_release_gate_is_safe_for_the_current_candidate():
    result = run("-Version", "v2.0.0", "-DryRun")
    if result.returncode == 0:
        assert "PASS DRY-RUN" in result.stdout
    else:
        assert "RELEASE REJECTED" in result.stderr


def test_release_gate_rejects_invalid_semver():
    result = run("-Version", "2.0.0", "-DryRun")
    assert result.returncode != 0
    assert "SemVer" in result.stderr


def test_release_script_is_read_only():
    content = SCRIPT.read_text(encoding="utf-8")
    assert "git tag" not in content
    assert "gh release create" not in content
    assert "git push" not in content


def test_release_contract_is_product_configured_not_template_hardcoded():
    content = SCRIPT.read_text(encoding="utf-8")
    policy = (ROOT / "release-policy.json").read_text(encoding="utf-8")
    assert "18-status-observabilidad" not in content
    assert "22-auditoria-release-v2" not in content
    assert "Get-ReleasePolicy" in content
    assert '"requireAllUnitsClosed": true' in policy


def test_release_policy_parser_ignores_example_fence_and_rejects_open_product_unit(tmp_path):
    policy_script = ROOT / "scripts" / "release-policy.ps1"
    roadmap = tmp_path / "ROADMAP.md"
    roadmap.write_text(
        "```text\n- [ ] 99-template-example\n```\n- [x] 01-real\n- [-] 02-open\n",
        encoding="utf-8",
    )
    command = (
        f'. "{policy_script}"; '
        f'$u=Get-ReleaseRoadmapUnits (Get-Content "{roadmap}" -Raw); '
        '"count=$($u.Count);slugs=$($u.Slug -join ",")"; '
        'try { Assert-ReleaseRoadmapComplete $u; exit 0 } '
        'catch { $_.Exception.Message; exit 1 }'
    )
    result = subprocess.run(["pwsh", "-NoProfile", "-Command", command], text=True, capture_output=True)
    assert result.returncode != 0
    assert "02-open" in result.stdout
    assert "99-template-example" not in result.stdout


def test_release_policy_parser_accepts_all_closed_product_units_without_template_phases(tmp_path):
    policy_script = ROOT / "scripts" / "release-policy.ps1"
    roadmap = tmp_path / "ROADMAP.md"
    roadmap.write_text(
        "```text\n- [ ] 99-template-example\n```\n- [x] 01-real\n- [x] 02-real\n",
        encoding="utf-8",
    )
    command = (
        f'. "{policy_script}"; '
        f'$u=Get-ReleaseRoadmapUnits (Get-Content "{roadmap}" -Raw); '
        'Assert-ReleaseRoadmapComplete $u; "PASS"'
    )
    result = subprocess.run(["pwsh", "-NoProfile", "-Command", command], text=True, capture_output=True)
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_release_readiness_keeps_audit_and_integrity_gates():
    content = SCRIPT.read_text(encoding="utf-8")
    assert "Falta evidencia de release" in content
    assert "check-integrity.ps1" in content
    assert "CI no verde" in content


def test_release_readiness_accepts_a_release_branch_derived_from_develop():
    content = SCRIPT.read_text(encoding="utf-8")
    assert 'merge-base", "--is-ancestor", $developSha, $candidateSha' in content
    assert 'remoteDevelop.Groups["sha"].Value -eq $developSha' in content
    assert 'candidateSha -eq $developSha' not in content
