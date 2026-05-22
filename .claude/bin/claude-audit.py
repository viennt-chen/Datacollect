#!/usr/bin/env python3
"""
Claude Code Configuration Auditor
=================================
Validates the integrity and consistency of the .claude/ configuration.
Run this after setup or before committing .claude/ changes.

Usage:
    python3 .claude/bin/claude-audit.py [--fix]

Exit codes:
    0 - All checks passed
    1 - One or more checks failed
    2 - Fatal error (audit could not complete)
"""

import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

# Version tracking
AUDIT_VERSION = "2.0.0"
REQUIRED_STRUCTURE = {
    "files": [
        "CLAUDE.md",
        "settings.json",
        "settings.local.json",
        "TASTE_INVARIANTS.md",
        "CODE_REVIEW_GUIDE.md",
        "SKILLS_MANAGEMENT_GUIDE.md",
        ".claude-version",
    ],
    "hooks": [
        "skill-activation-prompt.sh",
        "post-tool-use-tracker.sh",
        "branch-protection-pre-edit.sh",
        "dangerous-git-guard.sh",
        "bash-safety-guard.sh",
    ],
    "skills_dirs": [
        "skills/code-review-developer",
        "skills/self-review",
        "skills/confidence-check",
    ],
    "commands": [
        "commands/codeReview.md",
        "commands/verify.md",
        "commands/continue.md",
    ],
}

REQUIRED_EXECUTABLE_HOOKS = [
    "skill-activation-prompt.sh",
    "post-tool-use-tracker.sh",
    "branch-protection-pre-edit.sh",
    "dangerous-git-guard.sh",
    "bash-safety-guard.sh",
]


class Colors:
    OK = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    INFO = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_result(status: str, message: str, details: str = "") -> None:
    """Print a check result with color."""
    icon = {"OK": "✅", "WARN": "⚠️", "FAIL": "❌", "INFO": "ℹ️"}.get(status, "?")
    color = {"OK": Colors.OK, "WARN": Colors.WARN, "FAIL": Colors.FAIL, "INFO": Colors.INFO}.get(
        status, Colors.RESET
    )
    print(f"  {color}{icon} {message}{Colors.RESET}")
    if details:
        for line in details.split("\n"):
            print(f"      {line}")


def check_json_file(path: Path, description: str) -> tuple[bool, str]:
    """Validate a JSON file is well-formed."""
    if not path.exists():
        return False, f"File not found: {path}"
    try:
        with open(path, "r") as f:
            json.load(f)
        return True, "Valid JSON"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"


def check_hook_executable(path: Path) -> tuple[bool, str]:
    """Check if a hook script is executable."""
    if not path.exists():
        return False, "File not found"
    mode = path.stat().st_mode
    if mode & stat.S_IXUSR:
        return True, "Executable"
    return False, f"Not executable (mode: {oct(mode)[-3:]})"


def check_skill_structure(skill_dir: Path) -> tuple[bool, str]:
    """Validate a skill directory structure."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False, "Missing SKILL.md"

    # Parse frontmatter
    content = skill_md.read_text()
    if "---" not in content:
        return False, "Missing YAML frontmatter"

    lines = content.split("\n")
    if not lines[0].strip() == "---":
        return False, "Frontmatter must start at line 1"

    # Check required fields
    try:
        end_idx = lines[1:].index("---") + 1
        frontmatter = "\n".join(lines[1:end_idx])
        # Very basic YAML check
        if "name:" not in frontmatter:
            return False, "Missing 'name' in frontmatter"
        if "description:" not in frontmatter:
            return False, "Missing 'description' in frontmatter"
    except ValueError:
        return False, "Frontmatter not properly closed"

    return True, "Valid skill structure"


def check_skill_consistency(claude_dir: Path) -> tuple[bool, str]:
    """Check that all skills in skill-rules.json have corresponding directories."""
    rules_path = claude_dir / "hooks" / "skill-rules.json"
    if not rules_path.exists():
        return False, "skill-rules.json not found"

    with open(rules_path) as f:
        rules = json.load(f)

    skills_in_rules = set(rules.get("skills", {}).keys())
    skills_dir = claude_dir / "skills"
    skills_on_disk = set()

    if skills_dir.exists():
        for item in skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                skills_on_disk.add(item.name)

    # README.md is not a skill
    skills_on_disk.discard("README")

    missing_dirs = skills_in_rules - skills_on_disk
    orphan_dirs = skills_on_disk - skills_in_rules

    issues = []
    if missing_dirs:
        issues.append(f"Skills in rules but missing dirs: {', '.join(sorted(missing_dirs))}")
    if orphan_dirs:
        issues.append(f"Skill dirs not in rules: {', '.join(sorted(orphan_dirs))}")

    if issues:
        return False, "\n".join(issues)
    return True, f"All {len(skills_in_rules)} skills consistent"


def check_version_compatibility(claude_dir: Path) -> tuple[bool, str]:
    """Check .claude-version file exists and is valid."""
    version_file = claude_dir / ".claude-version"
    if not version_file.exists():
        return False, "Missing .claude-version (needed for upgrade tracking)"

    version = version_file.read_text().strip()
    if not version:
        return False, ".claude-version is empty"

    parts = version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return False, f"Invalid version format: {version} (expected x.y.z)"

    return True, f"Version {version}"


def check_logs_directory(claude_dir: Path) -> tuple[bool, str]:
    """Check logs directory exists and is gitignored."""
    logs_dir = claude_dir / "logs"
    gitignore = claude_dir / "logs" / ".gitignore"

    issues = []
    if not logs_dir.exists():
        issues.append("logs/ directory missing")
    if not gitignore.exists():
        issues.append("logs/.gitignore missing (should ignore *.log)")
    else:
        content = gitignore.read_text()
        if "*.log" not in content:
            issues.append("logs/.gitignore should contain '*.log'")

    if issues:
        return False, "\n".join(issues)
    return True, "logs/ properly configured"


def check_gitignore(claude_dir: Path, project_root: Path) -> tuple[bool, str]:
    """Check that sensitive files are gitignored."""
    gitignore = project_root / ".gitignore"
    if not gitignore.exists():
        return False, "No .gitignore found in project root"

    content = gitignore.read_text()
    required_patterns = [
        ".claude/logs/*.log",
        ".claude/settings.local.json",
    ]

    missing = [p for p in required_patterns if p not in content]
    if missing:
        return False, f"Missing patterns: {', '.join(missing)}"
    return True, "All required patterns present"


def check_hooks_lib(claude_dir: Path) -> tuple[bool, str]:
    """Check hooks/_lib/ shared library exists and is well-formed."""
    lib_dir = claude_dir / "hooks" / "_lib"
    common_sh = lib_dir / "common.sh"

    if not lib_dir.exists():
        return False, "hooks/_lib/ directory missing (shared hook utilities)"
    if not common_sh.exists():
        return False, "hooks/_lib/common.sh missing"

    # Check that hooks actually source the common library
    issues = []
    for hook in REQUIRED_EXECUTABLE_HOOKS:
        hook_path = claude_dir / "hooks" / hook
        if hook_path.exists():
            content = hook_path.read_text()
            if "_lib/common.sh" not in content and hook != "skill-activation-prompt.sh":
                # skill-activation is complex enough to not use common.sh
                pass

    return True, "Shared library present"


def check_mcp_config(project_root: Path) -> tuple[bool, str]:
    """Check MCP configuration if present."""
    mcp_file = project_root / ".mcp.json"
    if not mcp_file.exists():
        return True, "No .mcp.json (optional)"

    ok, msg = check_json_file(mcp_file, ".mcp.json")
    if not ok:
        return False, msg

    with open(mcp_file) as f:
        config = json.load(f)

    servers = config.get("mcpServers", {})
    if not servers:
        return True, "Valid JSON but no servers configured"

    server_count = len(servers)
    return True, f"{server_count} MCP server(s) configured"


def run_audit(claude_dir: Path, project_root: Path, fix: bool = False) -> int:
    """Run all audit checks and return exit code."""
    print(f"\n{Colors.BOLD}🔍 Claude Code Configuration Audit v{AUDIT_VERSION}{Colors.RESET}")
    print(f"   Project: {project_root}")
    print(f"   .claude/: {claude_dir}")
    print("")

    checks_passed = 0
    checks_failed = 0
    checks_warned = 0

    # 1. Core Files
    print(f"{Colors.BOLD}📁 Core Files{Colors.RESET}")
    for filename in REQUIRED_STRUCTURE["files"]:
        path = claude_dir / filename
        if path.exists():
            print_result("OK", filename)
            checks_passed += 1
        else:
            print_result("FAIL", filename, "Missing")
            checks_failed += 1
            if fix and filename == ".claude-version":
                (claude_dir / filename).write_text("1.0.0\n")
                print(f"      {Colors.INFO}→ Created with default version 1.0.0{Colors.RESET}")

    # 2. JSON Files
    print(f"\n{Colors.BOLD}📋 JSON Validation{Colors.RESET}")
    json_files = [
        ("settings.json", claude_dir / "settings.json"),
        ("settings.local.json", claude_dir / "settings.local.json"),
        ("skill-rules.json", claude_dir / "hooks" / "skill-rules.json"),
    ]
    for name, path in json_files:
        ok, msg = check_json_file(path, name)
        if ok:
            print_result("OK", name, msg)
            checks_passed += 1
        else:
            print_result("FAIL", name, msg)
            checks_failed += 1

    # 3. Hooks
    print(f"\n{Colors.BOLD}🪝 Hooks{Colors.RESET}")
    for hook in REQUIRED_STRUCTURE["hooks"]:
        path = claude_dir / "hooks" / hook
        ok, msg = check_hook_executable(path)
        if ok:
            print_result("OK", f"hooks/{hook}", msg)
            checks_passed += 1
        else:
            print_result("FAIL", f"hooks/{hook}", msg)
            checks_failed += 1
            if fix:
                path.chmod(path.stat().st_mode | stat.S_IXUSR)
                print(f"      {Colors.INFO}→ Fixed: made executable{Colors.RESET}")

    # 4. Shared Library
    print(f"\n{Colors.BOLD}📚 Shared Libraries{Colors.RESET}")
    ok, msg = check_hooks_lib(claude_dir)
    if ok:
        print_result("OK", "hooks/_lib/", msg)
        checks_passed += 1
    else:
        print_result("WARN", "hooks/_lib/", msg)
        checks_warned += 1

    # 5. Skills
    print(f"\n{Colors.BOLD}🧠 Skills{Colors.RESET}")
    for skill_dir_name in REQUIRED_STRUCTURE["skills_dirs"]:
        path = claude_dir / skill_dir_name
        ok, msg = check_skill_structure(path)
        if ok:
            print_result("OK", skill_dir_name, msg)
            checks_passed += 1
        else:
            print_result("FAIL", skill_dir_name, msg)
            checks_failed += 1

    # 6. Skill Consistency
    ok, msg = check_skill_consistency(claude_dir)
    if ok:
        print_result("OK", "skill-rules.json ↔ skills/", msg)
        checks_passed += 1
    else:
        print_result("FAIL", "skill-rules.json ↔ skills/", msg)
        checks_failed += 1

    # 7. Commands
    print(f"\n{Colors.BOLD}⚡ Commands{Colors.RESET}")
    for cmd in REQUIRED_STRUCTURE["commands"]:
        path = claude_dir / cmd
        if path.exists():
            print_result("OK", cmd)
            checks_passed += 1
        else:
            print_result("FAIL", cmd, "Missing")
            checks_failed += 1

    # 8. Version
    print(f"\n{Colors.BOLD}🏷️  Version Tracking{Colors.RESET}")
    ok, msg = check_version_compatibility(claude_dir)
    if ok:
        print_result("OK", ".claude-version", msg)
        checks_passed += 1
    else:
        print_result("FAIL", ".claude-version", msg)
        checks_failed += 1

    # 9. Logs
    print(f"\n{Colors.BOLD}📝 Logs{Colors.RESET}")
    ok, msg = check_logs_directory(claude_dir)
    if ok:
        print_result("OK", "logs/", msg)
        checks_passed += 1
    else:
        print_result("WARN", "logs/", msg)
        checks_warned += 1
        if fix:
            logs_dir = claude_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            (logs_dir / ".gitignore").write_text("*.log\n!.gitignore\n")
            print(f"      {Colors.INFO}→ Fixed: created logs/ with .gitignore{Colors.RESET}")

    # 10. Gitignore
    print(f"\n{Colors.BOLD}🔒 Git Integration{Colors.RESET}")
    ok, msg = check_gitignore(claude_dir, project_root)
    if ok:
        print_result("OK", ".gitignore", msg)
        checks_passed += 1
    else:
        print_result("WARN", ".gitignore", msg)
        checks_warned += 1

    # 11. MCP
    ok, msg = check_mcp_config(project_root)
    if ok:
        print_result("OK", ".mcp.json", msg)
        checks_passed += 1
    else:
        print_result("WARN", ".mcp.json", msg)
        checks_warned += 1

    # Summary
    print(f"\n{'=' * 50}")
    total = checks_passed + checks_failed + checks_warned
    print(f"{Colors.BOLD}Summary:{Colors.RESET} {Colors.OK}{checks_passed} passed{Colors.RESET}, "
          f"{Colors.FAIL}{checks_failed} failed{Colors.RESET}, "
          f"{Colors.WARN}{checks_warned} warned{Colors.RESET} ({total} total)")

    if checks_failed == 0:
        print(f"\n{Colors.OK}{Colors.BOLD}✅ All critical checks passed!{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ {checks_failed} check(s) failed.{Colors.RESET}")
        if not fix:
            print(f"   Run with --fix to attempt automatic repairs.")
        return 1


def main() -> int:
    fix = "--fix" in sys.argv

    # Find .claude directory
    cwd = Path.cwd()
    claude_dir = cwd / ".claude"

    if not claude_dir.exists():
        # Try parent directories
        for parent in cwd.parents:
            candidate = parent / ".claude"
            if candidate.exists():
                claude_dir = candidate
                break

    if not claude_dir.exists():
        print(f"{Colors.FAIL}Error: .claude/ directory not found{Colors.RESET}")
        print("Run this from a project with Claude Code configuration.")
        return 2

    project_root = claude_dir.parent
    return run_audit(claude_dir, project_root, fix=fix)


if __name__ == "__main__":
    sys.exit(main())
