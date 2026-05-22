#!/usr/bin/env python3
"""
Claude Code Admin Tool
======================
Unified management interface for .claude/ infrastructure.

Commands:
    audit       Run configuration health check
    upgrade     Upgrade configuration to latest scaffold version
    logs        Analyze skill activation logs
    skills      List and manage skills
    version     Show current configuration version

Usage:
    python3 .claude/bin/claude-admin.py <command> [options]
"""

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

ADMIN_VERSION = "2.0.0"
SCAFFOLD_LATEST = "2.0.0"


def find_claude_dir() -> Optional[Path]:
    """Find .claude directory from current working directory."""
    cwd = Path.cwd()
    claude_dir = cwd / ".claude"
    if claude_dir.exists():
        return claude_dir
    for parent in cwd.parents:
        candidate = parent / ".claude"
        if candidate.exists():
            return candidate
    return None


def get_current_version(claude_dir: Path) -> str:
    """Read current .claude configuration version."""
    version_file = claude_dir / ".claude-version"
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.0.0"


def cmd_audit(args) -> int:
    """Run the audit tool."""
    audit_script = Path(__file__).parent / "claude-audit.py"
    if not audit_script.exists():
        print("❌ claude-audit.py not found")
        return 1
    cmd = [sys.executable, str(audit_script)]
    if args.fix:
        cmd.append("--fix")
    return subprocess.call(cmd)


def cmd_upgrade(args) -> int:
    """Check for and perform configuration upgrades."""
    claude_dir = find_claude_dir()
    if not claude_dir:
        print("❌ .claude/ directory not found")
        return 1

    current = get_current_version(claude_dir)
    print(f"🔍 Current configuration version: {current}")
    print(f"📦 Latest scaffold version: {SCAFFOLD_LATEST}")

    if current == SCAFFOLD_LATEST:
        print("✅ Already up to date!")
        return 0

    # Parse versions
    current_parts = [int(p) for p in current.split(".")]
    latest_parts = [int(p) for p in SCAFFOLD_LATEST.split(".")]

    if current_parts >= latest_parts:
        print("✅ Configuration is newer than or equal to scaffold")
        return 0

    print(f"\n⚠️  Upgrade available: {current} → {SCAFFOLD_LATEST}")
    print("\nMigration steps:")

    # Version-specific migrations
    if current_parts[0] == 1:
        print("  1. Add .claude-version file")
        print("  2. Create bin/ directory with audit/admin tools")
        print("  3. Create memory/ directory for cross-session continuity")
        print("  4. Add hooks/_lib/common.sh for shared utilities")
        print("  5. Update settings.json with new PostToolUse formatter hook")

    print("\nRun with --apply to perform upgrade automatically.")

    if args.apply:
        print("\n🚀 Applying upgrade...")

        # Create version file
        version_file = claude_dir / ".claude-version"
        version_file.write_text(f"{SCAFFOLD_LATEST}\n")
        print(f"  ✅ Updated .claude-version to {SCAFFOLD_LATEST}")

        # Create bin/ directory
        bin_dir = claude_dir / "bin"
        bin_dir.mkdir(exist_ok=True)
        print("  ✅ Ensured bin/ directory exists")

        # Create memory/ directory
        memory_dir = claude_dir / "memory"
        for subdir in ["decisions", "sessions"]:
            (memory_dir / subdir).mkdir(parents=True, exist_ok=True)
        print("  ✅ Ensured memory/ directory structure")

        # Create hooks/_lib/
        lib_dir = claude_dir / "hooks" / "_lib"
        lib_dir.mkdir(exist_ok=True)
        common_sh = lib_dir / "common.sh"
        if not common_sh.exists():
            common_sh.write_text("""#!/bin/bash
# Common utilities for Claude Code hooks
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../../logs"

ensure_log_dir() { mkdir -p "$LOG_DIR"; }
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }
""")
        print("  ✅ Ensured hooks/_lib/common.sh")

        print(f"\n✅ Upgrade to {SCAFFOLD_LATEST} complete!")
        print("Run 'python3 .claude/bin/claude-admin.py audit' to verify.")

    return 0


def cmd_logs(args) -> int:
    """Analyze skill activation logs."""
    claude_dir = find_claude_dir()
    if not claude_dir:
        print("❌ .claude/ directory not found")
        return 1

    log_file = claude_dir / "logs" / "skill-activations.log"
    if not log_file.exists():
        print("❌ No skill activation logs found")
        print("   Run some tasks first to generate logs.")
        return 1

    lines = log_file.read_text().split("\n")

    # Count activations by skill
    skill_counts = Counter()
    excluded_counts = Counter()
    missed_count = 0

    for line in lines:
        if "Matched:" in line:
            skill = line.split("Matched:")[1].split("(")[0].strip()
            skill_counts[skill] += 1
        elif "Excluded:" in line:
            skill = line.split("Excluded:")[1].split("(")[0].strip()
            excluded_counts[skill] += 1
        elif "No skills matched" in line:
            missed_count += 1

    print("📊 Skill Activation Analysis")
    print("=" * 40)
    print(f"Total log entries: {len(lines)}")
    print(f"Missed activations: {missed_count}")
    print("")

    if skill_counts:
        print("Top activated skills:")
        for skill, count in skill_counts.most_common(10):
            print(f"  {count:4d}  {skill}")

    if excluded_counts and args.verbose:
        print("\nExcluded skills:")
        for skill, count in excluded_counts.most_common():
            print(f"  {count:4d}  {skill}")

    return 0


def cmd_skills(args) -> int:
    """List and manage skills."""
    claude_dir = find_claude_dir()
    if not claude_dir:
        print("❌ .claude/ directory not found")
        return 1

    skills_dir = claude_dir / "skills"
    if not skills_dir.exists():
        print("❌ skills/ directory not found")
        return 1

    print("📚 Skills Inventory")
    print("=" * 50)

    for item in sorted(skills_dir.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text()
                # Extract description from frontmatter
                desc = "No description"
                if "description:" in content:
                    for line in content.split("\n"):
                        if line.strip().startswith("description:"):
                            desc = line.split("description:", 1)[1].strip().strip('"')
                            break
                print(f"  📄 {item.name}")
                print(f"     {desc}")

    # Read skill-rules.json
    rules_file = claude_dir / "hooks" / "skill-rules.json"
    if rules_file.exists():
        with open(rules_file) as f:
            rules = json.load(f)
        print(f"\n  Total skills in rules: {len(rules.get('skills', {}))}")
        print(f"  Max skills per prompt: {rules.get('config', {}).get('maxSkillsPerPrompt', 2)}")

    return 0


def cmd_version(args) -> int:
    """Show version information."""
    claude_dir = find_claude_dir()

    print(f"Claude Code Admin Tool: v{ADMIN_VERSION}")
    print(f"Latest Scaffold: v{SCAFFOLD_LATEST}")

    if claude_dir:
        current = get_current_version(claude_dir)
        print(f"Current Project Config: v{current}")

        if current != SCAFFOLD_LATEST:
            print(f"\n⚠️  Upgrade available: {current} → {SCAFFOLD_LATEST}")
            print("Run: python3 .claude/bin/claude-admin.py upgrade")
    else:
        print("No .claude/ configuration found in current directory")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Claude Code Infrastructure Admin Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s audit              Run health check
  %(prog)s audit --fix        Run health check and auto-fix issues
  %(prog)s upgrade            Check for available upgrades
  %(prog)s upgrade --apply    Apply available upgrades
  %(prog)s logs               Analyze activation logs
  %(prog)s logs --verbose     Show detailed log analysis
  %(prog)s skills             List all skills
  %(prog)s version            Show version info
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # audit
    audit_parser = subparsers.add_parser("audit", help="Run configuration health check")
    audit_parser.add_argument("--fix", action="store_true", help="Auto-fix issues")

    # upgrade
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade configuration")
    upgrade_parser.add_argument("--apply", action="store_true", help="Apply upgrade")

    # logs
    logs_parser = subparsers.add_parser("logs", help="Analyze skill activation logs")
    logs_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # skills
    subparsers.add_parser("skills", help="List and manage skills")

    # version
    subparsers.add_parser("version", help="Show version information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "audit": cmd_audit,
        "upgrade": cmd_upgrade,
        "logs": cmd_logs,
        "skills": cmd_skills,
        "version": cmd_version,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
