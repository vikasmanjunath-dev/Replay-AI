import shutil
import subprocess
import sys
from pathlib import Path

from main import get_benchmark_scenarios


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEMO_STORE = REPOSITORY_ROOT / "demo-store"


def _run_checkout_tests(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/test_checkout.py"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_checkout_scenario_uses_the_seeded_repository_files():
    scenario = next(
        item for item in get_benchmark_scenarios()
        if item["id"] == "scenario_checkout_discount_twice"
    )

    assert scenario["codebase"] == {
        filename: (DEMO_STORE / filename).read_text(encoding="utf-8")
        for filename in ("src/__init__.py", "src/checkout.py", "tests/test_checkout.py")
    }
    assert "$100 cart should total $90.00" in scenario["bug_report"]


def test_seeded_discount_regression_fails_then_fixed_checkout_passes(tmp_path):
    baseline = _run_checkout_tests(DEMO_STORE)
    assert baseline.returncode != 0
    assert "test_discount_code_is_applied_once" in baseline.stdout
    assert "1 failed, 1 passed" in baseline.stdout

    fixed_copy = tmp_path / "demo-store"
    shutil.copytree(DEMO_STORE, fixed_copy)
    patch = DEMO_STORE / "patches" / "discount-once.patch"
    checked = subprocess.run(
        ["git", "apply", "--check", "--recount", str(patch)],
        cwd=fixed_copy,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert checked.returncode == 0, checked.stderr
    applied = subprocess.run(
        ["git", "apply", "--recount", str(patch)],
        cwd=fixed_copy,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert applied.returncode == 0, applied.stderr

    fixed = _run_checkout_tests(fixed_copy)
    assert fixed.returncode == 0, fixed.stdout + fixed.stderr
    assert "2 passed" in fixed.stdout
