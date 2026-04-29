#!/usr/bin/env python3
"""Fast pre-commit rule checker — pure Python regex checks on staged files.

Designed for sub-second execution as a git pre-commit hook.
For the full rule suite, use scripts/code_rules.py.

Usage:
    python scripts/code_rules_fast.py            # Check staged files
    python scripts/code_rules_fast.py --all      # Check all module files
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Violation:
    rule_id: str
    severity: str
    file: str
    line: int
    message: str


# ── Checks ────────────────────────────────────────────────────────────────


def check_file_size(path: Path, rel: str) -> list[Violation]:
    """002.1 — Python files must not exceed 1000 lines."""
    if not rel.startswith("modules/"):
        return []
    lines = path.read_text().splitlines()
    if len(lines) > 1000:
        return [
            Violation(
                "002.1",
                "error",
                rel,
                1,
                f"File has {len(lines)} lines (limit: 1000)",
            )
        ]
    return []


def check_relative_imports(path: Path, rel: str) -> list[Violation]:
    """001.1 — No relative imports anywhere in modules/."""
    if not rel.startswith("modules/"):
        return []
    violations = []
    pattern = re.compile(r"^\s*from\s+\.")
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if pattern.match(line):
            violations.append(
                Violation(
                    "001.1",
                    "error",
                    rel,
                    i,
                    "Relative import — use absolute: from modules.backend.xxx import ...",
                )
            )
    return violations


def check_direct_logging(path: Path, rel: str) -> list[Violation]:
    """001.2 — No direct import logging — use get_logger()."""
    if not rel.startswith("modules/"):
        return []
    if "core/logging.py" in rel:
        return []
    violations = []
    pattern = re.compile(r"^import logging\s*$")
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if pattern.match(line):
            violations.append(
                Violation(
                    "001.2",
                    "error",
                    rel,
                    i,
                    "Direct import logging — use get_logger() from core.logging",
                )
            )
    return violations


def check_bare_except(path: Path, rel: str) -> list[Violation]:
    """002.2 — No bare except: clauses."""
    violations = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if re.match(r"^\s*except\s*:", line):
            violations.append(
                Violation(
                    "002.2",
                    "warning",
                    rel,
                    i,
                    "Bare except: clause",
                )
            )
    return violations


def check_swallowed_exception(path: Path, rel: str) -> list[Violation]:
    """002.3 — No except Exception/BaseException followed by pass."""
    violations = []
    lines = path.read_text().splitlines()
    for i, line in enumerate(lines):
        if re.match(r"\s*except\s+(Exception|BaseException)", line):
            if i + 1 < len(lines) and lines[i + 1].strip() == "pass":
                violations.append(
                    Violation(
                        "002.3",
                        "error",
                        rel,
                        i + 1,
                        "Swallowed exception: except Exception/BaseException with pass",
                    )
                )
    return violations


def check_datetime_violations(path: Path, rel: str) -> list[Violation]:
    """004.x — No datetime.now(), utcnow(), or timezone-aware patterns."""
    if not rel.startswith("modules/"):
        return []
    violations = []
    now_pattern = re.compile(r"datetime\.(now\(\)|utcnow\(\))")
    tz_pattern = re.compile(r"(pytz\.|datetime\.now\(timezone\.utc\)|\.astimezone|\.localize\()")
    skip_line = re.compile(r"(replace\(tzinfo=None\)|#\s|^\s*\"\"\")")
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if skip_line.search(line):
            continue
        if now_pattern.search(line):
            violations.append(
                Violation(
                    "004.1",
                    "error",
                    rel,
                    i,
                    "datetime.now()/utcnow() — use utc_now() from core.utils",
                )
            )
        elif tz_pattern.search(line):
            violations.append(
                Violation(
                    "004.2",
                    "error",
                    rel,
                    i,
                    "Timezone-aware datetime — use naive UTC via utc_now()",
                )
            )
    return violations


def check_hardcoded_secrets(path: Path, rel: str) -> list[Violation]:
    """003.1 — No hardcoded secrets in source code."""
    if not rel.startswith("modules/"):
        return []
    violations = []
    pattern = re.compile(r"""(api_key|password|token|secret)\s*=\s*['"][^'"]{10,}['"]""", re.I)
    skip = re.compile(
        r"(os\.getenv|\.env|env\.example|your_|settings\.|Field\(|test_|TEST_|conftest)"
    )
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if pattern.search(line) and not skip.search(line):
            violations.append(
                Violation(
                    "003.1",
                    "error",
                    rel,
                    i,
                    "Possible hardcoded secret",
                )
            )
    return violations


def check_api_imports_repositories(path: Path, rel: str) -> list[Violation]:
    """001.3 — API layer must not import repositories directly."""
    if not rel.startswith("modules/backend/api/"):
        return []
    violations = []
    pattern = re.compile(r"from modules\.backend\.repositories\.")
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if pattern.search(line):
            violations.append(
                Violation(
                    "001.3",
                    "error",
                    rel,
                    i,
                    "API endpoint imports repository directly — use a service",
                )
            )
    return violations


def check_telegram_imports_models(path: Path, rel: str) -> list[Violation]:
    """001.4 — Telegram handlers must not import models or repositories."""
    if not rel.startswith("modules/telegram/"):
        return []
    violations = []
    pattern = re.compile(r"from modules\.backend\.(models|repositories)\.")
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if pattern.search(line):
            violations.append(
                Violation(
                    "001.4",
                    "error",
                    rel,
                    i,
                    "Telegram handler imports models/repositories — use a service",
                )
            )
    return violations


def check_endpoint_orchestration(path: Path, rel: str) -> list[Violation]:
    """001.6 — API endpoints must not contain multi-service orchestration."""
    if not rel.startswith("modules/backend/api/"):
        return []
    violations = []
    lines = path.read_text().splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(("#", "from ", "import ", '"""', "'''")):
            continue
        if "asyncio.gather(" in line:
            violations.append(
                Violation(
                    "001.6",
                    "warning",
                    rel,
                    i,
                    "asyncio.gather in endpoint — move orchestration to a service",
                )
            )
    return violations


def check_endpoint_inline_transforms(path: Path, rel: str) -> list[Violation]:
    """001.7 — API endpoints must not build response dicts with computed fields."""
    if not rel.startswith("modules/backend/api/"):
        return []
    violations = []
    compute_pattern = re.compile(
        r"""["']\w+["']\s*:\s*"""
        r"(len\(\w+\.\w+"
        r"|sum\(|max\(|min\("
        r"|\w+\.\w+\s*[-+*/]\s*\w+)"
    )
    for i, line in enumerate(path.read_text().splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(("#", "from ", "import ", '"""', "'''")):
            continue
        if compute_pattern.search(line):
            violations.append(
                Violation(
                    "001.7",
                    "warning",
                    rel,
                    i,
                    "Computed field in endpoint response — move to model property or service",
                )
            )
    return violations


def check_os_getenv_fallback(path: Path, rel: str) -> list[Violation]:
    """003.3 — No os.getenv() with hardcoded fallback defaults."""
    if not rel.startswith("modules/"):
        return []
    if any(s in rel for s in ("compliance.py", "test_", "conftest")):
        return []
    violations = []
    pattern = re.compile(r"os\.(getenv|environ\.get)\s*\(.+,\s*['\"]")
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if pattern.search(line):
            violations.append(
                Violation(
                    "003.3",
                    "error",
                    rel,
                    i,
                    "os.getenv() with hardcoded fallback — use get_settings() or get_app_config()",
                )
            )
    return violations


ALL_CHECKS = [
    check_file_size,
    check_relative_imports,
    check_direct_logging,
    check_bare_except,
    check_swallowed_exception,
    check_datetime_violations,
    check_hardcoded_secrets,
    check_os_getenv_fallback,
    check_api_imports_repositories,
    check_telegram_imports_models,
    check_endpoint_orchestration,
    check_endpoint_inline_transforms,
]


# ── File discovery ────────────────────────────────────────────────────────


def get_staged_py_files() -> list[Path]:
    """Get staged Python files from git."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    return [PROJECT_ROOT / f for f in result.stdout.strip().splitlines() if f.endswith(".py")]


def get_all_module_files() -> list[Path]:
    """Get all Python files under modules/."""
    return sorted((PROJECT_ROOT / "modules").rglob("*.py"))


# ── Output ────────────────────────────────────────────────────────────────


RED = "\033[31m"
YEL = "\033[33m"
RST = "\033[0m"
BOLD = "\033[1m"


def main() -> int:
    parser = argparse.ArgumentParser(description="Fast pre-commit rule checker")
    parser.add_argument("--all", action="store_true", help="Check all module files")
    args = parser.parse_args()

    files = get_all_module_files() if args.all else get_staged_py_files()
    if not files:
        return 0

    all_violations: list[Violation] = []
    for path in files:
        if not path.exists():
            continue
        rel = str(path.relative_to(PROJECT_ROOT))
        for check_fn in ALL_CHECKS:
            all_violations.extend(check_fn(path, rel))

    errors = [v for v in all_violations if v.severity == "error"]
    warnings = [v for v in all_violations if v.severity == "warning"]

    if errors:
        print(f"\n{RED}{BOLD}Pre-commit check failed ({len(errors)} errors){RST}\n")
        for v in sorted(errors, key=lambda x: (x.rule_id, x.file)):
            print(f"  {RED}[{v.rule_id}]{RST} {v.file}:{v.line} — {v.message}")

    if warnings:
        print(f"\n{YEL}Warnings ({len(warnings)}):{RST}")
        for v in sorted(warnings, key=lambda x: (x.rule_id, x.file)):
            print(f"  {YEL}[{v.rule_id}]{RST} {v.file}:{v.line} — {v.message}")

    if errors:
        print(f"\n{RED}Commit blocked. Fix errors above or use --no-verify to skip.{RST}")
        return 1

    if all_violations:
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
