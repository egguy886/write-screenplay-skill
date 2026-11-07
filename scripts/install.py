#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Write-Screenplay Skill Installer / Bridge Script
Automatically links or copies this skill into:
- Google Antigravity IDE (Global ~/.gemini/config/skills/ & Workspace .agents/skills/)
- Universal Agents (~/.agents/skills/)
- Claude Code (~/.claude/skills/)
- Codex CLI (~/.codex/skills/)
"""

import os
import sys
import shutil
from pathlib import Path

SKILL_NAME = "write-screenplay"
CURRENT_DIR = Path(__file__).resolve().parent.parent

def get_target_directories():
    home = Path.home()
    targets = [
        # Google Antigravity IDE Global Config
        home / ".gemini" / "config" / "skills" / SKILL_NAME,
        # Universal Agent skills directory (used by Doubao, Trae Solo, Codex, etc.)
        home / ".agents" / "skills" / SKILL_NAME,
        # Claude Code
        home / ".claude" / "skills" / SKILL_NAME,
        # Codex CLI
        home / ".codex" / "skills" / SKILL_NAME,
        # Local Workspace .agents/skills/write-screenplay (if inside a project workspace)
        CURRENT_DIR.parent / ".agents" / "skills" / SKILL_NAME,
    ]
    return targets

def install_skill():
    print(f"=== Installing/Bridging '{SKILL_NAME}' ===")
    print(f"Source Directory: {CURRENT_DIR}")

    targets = get_target_directories()

    for target in targets:
        try:
            target_parent = target.parent
            target_parent.mkdir(parents=True, exist_ok=True)

            # If existing link or file, clean up; if directory, overlay non-git files cleanly (avoids Windows .git WinError 5)
            if target.is_symlink() or target.is_file():
                target.unlink()

            if not target.exists():
                try:
                    target.symlink_to(CURRENT_DIR, target_is_directory=True)
                    print(f"[SUCCESS] Symlinked to: {target}")
                    continue
                except (OSError, NotImplementedError):
                    pass

            shutil.copytree(
                CURRENT_DIR,
                target,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'),
            )
            print(f"[SUCCESS] Synced to: {target}")

        except Exception as e:
            print(f"[WARN] Failed to install to {target}: {e}")

    print("\nInstallation complete! You can now use /写剧本 in your favorite Agent.")

if __name__ == "__main__":
    install_skill()
