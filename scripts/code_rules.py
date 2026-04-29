#!/usr/bin/env python3
"""Enforce codebase rules defined in docs/04-rules/*.jsonl.

Reads machine-verifiable rules, executes each check command, and reports
pass/fail with an exit code suitable for CI and pre-commit hooks.

Review-only rules (check="review") are listed but not executed.

Usage:
    python scripts/code_rules.py                      # Run all rules
    python scripts/code_rules.py --severity error      # Errors only
    python scripts/code_rules.py --rule-file 002       # Rules from one file
    python scripts/code_rules.py --rule 001.6          # Single rule
    python scripts/code_rules.py --fix                 # Show fix instructions
    python scripts/code_rules.py --json                # JSON output
    python scripts/code_rules.py --staged              # Only mention staged files
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = PROJECT_ROOT / "docs" / "04-rules"


# ── Data types ────────────────────────────────────────────────────────────


@dataclass
class Rule:
    id: str
    severity: str
    description: str
    scope: str
    check: str
    expect: str
    fix: str
    category: str = ""


@dataclass
class RuleResult:
    rule: Rule
    passed: bool
    output: str = ""
    error: str = ""


# ── Rule loading ──────────────────────────────────────────────────────────


def load_rules(rule_file_filter: str = "", rule_id_filter: str = "") -> list[Rule]:
    """Load rules from all JSONL files in docs/04-rules/."""
    rules: list[Rule] = []
    for path in sorted(RULES_DIR.glob("*.jsonl")):
        if rule_file_filter and rule_file_filter not in path.name:
            continue
        for line_text in path.read_text().splitlines():
            line_text = line_text.strip()
            if not line_text:
                continue
            try:
                data = json.loads(line_text)
            except json.JSONDecodeError:
                continue
            rule = Rule(
                id=data.get("id", "?"),
                severity=data.get("severity", "warning"),
                description=data.get("description", ""),
                scope=data.get("scope", ""),
                check=data.get("check", "review"),
                expect=data.get("expect", "zero_results"),
                fix=data.get("fix", ""),
                category=data.get("category", ""),
            )
            if rule_id_filter and rule.id != rule_id_filter:
                continue
            rules.append(rule)
    return rules


# ── Rule execution ────────────────────────────────────────────────────────


def run_rule(rule: Rule) -> RuleResult:
    """Execute a single rule's check command and evaluate against expect."""
    if rule.check == "review":
        return RuleResult(rule=rule, passed=True, output="(review-only)")

    try:
        result = subprocess.run(
            rule.check,
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        output = (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return RuleResult(rule=rule, passed=False, error="Check timed out (30s)")
    except Exception as e:
        return RuleResult(rule=rule, passed=False, error=str(e))

    passed = evaluate_expectation(rule.expect, output, result.returncode)
    return RuleResult(rule=rule, passed=passed, output=output)


def evaluate_expectation(expect: str, output: str, returncode: int) -> bool:
    """Evaluate whether the check output matches the expectation."""
    if expect == "zero_results":
        return not output.strip()
    if expect == "at_least_one":
        return bool(output.strip())
    if expect.startswith("contains:"):
        expected_text = expect[len("contains:") :]
        return expected_text in output
    # Exact match
    return output.strip() == expect.strip()


# ── Output formatting ─────────────────────────────────────────────────────


RED = "\033[31m"
GRN = "\033[32m"
YEL = "\033[33m"
DIM = "\033[2m"
RST = "\033[0m"
BOLD = "\033[1m"

SEVERITY_COLOR = {"error": RED, "warning": YEL, "info": DIM}


def format_human(results: list[RuleResult], show_fix: bool = False) -> str:
    """Format results as a human-readable table."""
    lines: list[str] = []
    lines.append(f"\n{'':>6}  {'Sev':<8}  {'Rule':<8}  {'Description':<60}  {'Status'}")
    lines.append("\u2500" * 100)

    passed_count = 0
    failed_count = 0
    review_count = 0

    for r in results:
        if r.output == "(review-only)":
            review_count += 1
            status = f"{DIM}review{RST}"
        elif r.passed:
            passed_count += 1
            status = f"{GRN}pass{RST}"
        else:
            failed_count += 1
            color = SEVERITY_COLOR.get(r.rule.severity, RST)
            status = f"{color}{BOLD}FAIL{RST}"

        sev_color = SEVERITY_COLOR.get(r.rule.severity, RST)
        desc = r.rule.description[:58]
        lines.append(
            f"  {sev_color}{r.rule.severity:<8}{RST}  " f"{r.rule.id:<8}  {desc:<60}  {status}"
        )

        if not r.passed and r.output and r.output != "(review-only)":
            for output_line in r.output.splitlines()[:5]:
                lines.append(f"{'':>20}{DIM}{output_line}{RST}")
            if len(r.output.splitlines()) > 5:
                lines.append(f"{'':>20}{DIM}... ({len(r.output.splitlines()) - 5} more){RST}")

        if show_fix and not r.passed and r.rule.fix:
            lines.append(f"{'':>20}{YEL}Fix: {r.rule.fix}{RST}")

    lines.append("\u2500" * 100)
    lines.append(
        f"  {GRN}{passed_count} passed{RST}  "
        f"{RED}{failed_count} failed{RST}  "
        f"{DIM}{review_count} review-only{RST}  "
        f"({len(results)} total)"
    )

    return "\n".join(lines)


def format_json(results: list[RuleResult]) -> str:
    """Format results as JSON."""
    items = []
    for r in results:
        items.append(
            {
                "rule_id": r.rule.id,
                "severity": r.rule.severity,
                "description": r.rule.description,
                "passed": r.passed,
                "output": r.output if not r.passed else "",
                "fix": r.rule.fix if not r.passed else "",
            }
        )
    return json.dumps({"results": items, "total": len(items)}, indent=2)


# ── Main ──────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce codebase rules from JSONL definitions")
    parser.add_argument(
        "--severity", choices=["error", "warning", "info"], help="Filter by severity"
    )
    parser.add_argument("--rule-file", default="", help="Filter by rule file name (e.g., '002')")
    parser.add_argument("--rule", default="", help="Run a single rule by ID (e.g., '001.6')")
    parser.add_argument("--fix", action="store_true", help="Show fix instructions for failures")
    parser.add_argument("--json", action="store_true", dest="json_output", help="JSON output")
    args = parser.parse_args()

    rules = load_rules(rule_file_filter=args.rule_file, rule_id_filter=args.rule)
    if not rules:
        print("No rules found.")
        return 0

    if args.severity:
        rules = [r for r in rules if r.severity == args.severity]

    results: list[RuleResult] = []
    for rule in rules:
        results.append(run_rule(rule))

    if args.json_output:
        print(format_json(results))
    else:
        print(format_human(results, show_fix=args.fix))

    errors = sum(1 for r in results if not r.passed and r.rule.severity == "error")
    if errors > 0:
        print(f"\n{RED}{errors} error(s) found. Fix before committing.{RST}\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
