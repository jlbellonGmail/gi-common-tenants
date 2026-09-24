from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_reconciliation_requires_merged_pr_and_expected_base_and_branch():
    script = read("scripts/reconcile-merged-feature.ps1")
    assert 'if ($pr.state -ne "MERGED")' in script
    assert 'if ($pr.baseRefName -ne $BaseBranch)' in script
    assert 'if ($pr.headRefName -ne $Branch)' in script
    assert "merge-base --is-ancestor" in script


def test_reconciliation_requires_human_review_integrity_and_ci():
    script = read("scripts/reconcile-merged-feature.ps1")
    assert "human-authorization.md" in script
    assert "GI-SINGLEMAINTAINER-GATE" in script
    assert "issues/$PrNumber/comments" in script
    assert "headRefOid" in script
    assert "independent-review.md" in script
    assert "integrity-evidence.md" in script
    for job in ("circuit-tests", "product-tests", "local-reconciler-tests"):
        assert job in script
    assert 'conclusion -ne "SUCCESS"' in script


def test_reconciliation_is_safe_for_pending_ready_and_idempotent_done_states():
    script = read("scripts/reconcile-merged-feature.ps1")
    assert "if ($state -eq \"x\")" in script
    assert "if ($state -notin @(' ', '-'))" in script
    assert "'- [x] $1'" in script


def test_post_hitl_does_not_depend_on_closed_event_for_normal_merge():
    workflow = read(".github/workflows/post-hitl-merge-gate.yml")
    assert "reconcile-merged-feature.ps1" in workflow
    assert "git worktree add --detach" in workflow


def test_merge_gate_publishes_evidence_consumable_after_merge():
    script = read("scripts/complete-approved-pr.ps1")
    assert "Add-GateEvidenceComment" in script
    assert "GI-SINGLEMAINTAINER-GATE" in script
    assert '"pr", "comment"' in script
    assert "authorizationSource" in script


def test_manual_post_merge_dispatch_exists_for_recovery():
    workflow = read(".github/workflows/post-merge-close-feature.yml")
    assert "workflow_dispatch:" in workflow
    assert "reconcile-merged-feature.ps1" in workflow
