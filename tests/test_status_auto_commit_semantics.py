import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
UPDATE = ROOT / "scripts" / "update-status.ps1"
CHECK = ROOT / "scripts" / "check-status.ps1"


def powershell():
    for name in ("pwsh", "powershell.exe", "powershell"):
        path = shutil.which(name)
        if path:
            return path
    pytest.skip("PowerShell no disponible")


def env():
    result = os.environ.copy()
    result["GIT_CONFIG_GLOBAL"] = "NUL" if os.name == "nt" else "/dev/null"
    result["GIT_TERMINAL_PROMPT"] = "0"
    return result


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=True, env=env())


def run(script, repo):
    return subprocess.run(
        [powershell(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
        cwd=repo,
        text=True,
        capture_output=True,
        env=env(),
    )


def make_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "checkout", "-b", "develop")
    git(repo, "config", "user.email", "tests@example.invalid")
    git(repo, "config", "user.name", "Tests")
    (repo / "STATUS.md").write_text("# Manual\n", encoding="utf-8")
    git(repo, "add", "STATUS.md")
    git(repo, "commit", "-m", "initial")
    return repo


def commit_status(repo):
    git(repo, "add", "STATUS.md")
    git(repo, "commit", "-m", "chore: sincronizar STATUS")


def test_status_only_automatic_commit_is_not_stale(tmp_path):
    repo = make_repo(tmp_path)
    assert run(UPDATE, repo).returncode == 0
    commit_status(repo)
    result = run(CHECK, repo)
    assert result.returncode == 0
    assert "STALE HEAD" not in result.stdout


def test_functional_commit_after_snapshot_remains_stale(tmp_path):
    repo = make_repo(tmp_path)
    assert run(UPDATE, repo).returncode == 0
    commit_status(repo)
    (repo / "functional.txt").write_text("functional change\n", encoding="utf-8")
    git(repo, "add", "functional.txt")
    git(repo, "commit", "-m", "feat: functional change")
    result = run(CHECK, repo)
    assert result.returncode == 0
    assert "STALE HEAD" in result.stdout


def test_real_stale_snapshot_is_detected(tmp_path):
    repo = make_repo(tmp_path)
    assert run(UPDATE, repo).returncode == 0
    status = repo / "STATUS.md"
    status.write_text(status.read_text(encoding="utf-8").replace("- HEAD: ", "- HEAD: deadbeef\n# old: ", 1), encoding="utf-8")
    result = run(CHECK, repo)
    assert result.returncode == 0
    assert "STALE HEAD" in result.stdout


def test_snapshot_from_another_branch_is_inconsistent(tmp_path):
    repo = make_repo(tmp_path)
    assert run(UPDATE, repo).returncode == 0
    git(repo, "checkout", "-b", "feature/99-demo")
    result = run(CHECK, repo)
    assert result.returncode == 1
    assert "rama no coincide" in result.stdout
