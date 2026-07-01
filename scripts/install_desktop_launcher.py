#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path


APP_ID = "ai-workflow-risk-auditor-pro.desktop"
APP_NAME = "AI Workflow Risk Auditor Pro"


def desktop_exec_quote(path: Path) -> str:
    value = str(path.resolve()).replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("$", "\\$")
    return f'"{value}"'


def build_desktop_entry(project_dir: Path, terminal: bool = False) -> str:
    project_dir = project_dir.resolve()
    helper = project_dir / "scripts" / "launch_aiwra.sh"
    icon = project_dir / "assets" / "aiwra_icon.svg"
    return "\n".join(
        [
            "[Desktop Entry]",
            "Type=Application",
            "Version=1.0",
            f"Name={APP_NAME}",
            "Comment=Local-first deterministic AI workflow risk command center",
            f"Exec={desktop_exec_quote(helper)}",
            f"Icon={icon}",
            f"Path={project_dir}",
            f"Terminal={'true' if terminal else 'false'}",
            "Categories=Development;Utility;Security;",
            "Keywords=AI;risk;audit;workflow;local;",
            "StartupNotify=true",
            "StartupWMClass=streamlit",
            "",
        ]
    )


def write_launcher(destination: Path, content: str) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    previous = destination.read_text(encoding="utf-8") if destination.exists() else None
    destination.write_text(content, encoding="utf-8")
    destination.chmod(0o755)
    return previous != content


def remove_launcher(destination: Path) -> bool:
    if not destination.exists():
        return False
    destination.unlink()
    return True


def validate_project(project_dir: Path) -> None:
    required = [
        project_dir,
        project_dir / "app.py",
        project_dir / "scripts" / "launch_aiwra.sh",
        project_dir / "assets" / "aiwra_icon.svg",
        project_dir / ".venv" / "bin" / "python",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError("Missing required path(s): " + ", ".join(missing))
    python = project_dir / ".venv" / "bin" / "python"
    result = subprocess.run(
        [str(python), "-c", "import streamlit"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError("Streamlit is unavailable in .venv. Install requirements before creating the launcher.")


def default_applications_dir() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "applications"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install or remove the local AIWRA Linux desktop launcher.")
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--applications-dir", type=Path, default=default_applications_dir())
    parser.add_argument("--desktop", action="store_true", help="Also create a shortcut in ~/Desktop when that directory exists.")
    parser.add_argument("--desktop-dir", type=Path, default=Path.home() / "Desktop")
    parser.add_argument("--terminal", action="store_true", help="Keep a terminal window visible while Streamlit runs.")
    parser.add_argument("--uninstall", action="store_true", help="Remove launchers created by this script.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app_destination = args.applications_dir.expanduser() / APP_ID
    desktop_destination = args.desktop_dir.expanduser() / f"{APP_NAME}.desktop"

    if args.uninstall:
        removed = [path for path in (app_destination, desktop_destination) if remove_launcher(path)]
        if removed:
            print("Removed AIWRA launcher(s):")
            for path in removed:
                print(f"  {path}")
        else:
            print("No AIWRA desktop launcher was installed at the expected user-local paths.")
        return 0

    project_dir = args.project_dir.expanduser().resolve()
    try:
        validate_project(project_dir)
    except RuntimeError as exc:
        print(f"Cannot install launcher: {exc}", file=sys.stderr)
        return 1

    helper = project_dir / "scripts" / "launch_aiwra.sh"
    helper.chmod(helper.stat().st_mode | 0o111)
    content = build_desktop_entry(project_dir, terminal=args.terminal)
    changed = write_launcher(app_destination, content)
    print(f"{'Installed' if changed else 'Verified'} application launcher: {app_destination}")

    if args.desktop:
        if not args.desktop_dir.expanduser().is_dir():
            print(f"Desktop directory does not exist; skipped desktop shortcut: {args.desktop_dir.expanduser()}")
        else:
            desktop_changed = write_launcher(desktop_destination, content)
            print(f"{'Installed' if desktop_changed else 'Verified'} desktop shortcut: {desktop_destination}")

    print("Launch it from your desktop application menu.")
    print("The app binds to http://127.0.0.1:8501 and does not require sudo.")
    print("Logs: ${XDG_STATE_HOME:-$HOME/.local/state}/aiwra/aiwra-launch.log")
    print(f"Remove: {shlex.quote(str(Path(sys.executable)))} {shlex.quote(str(Path(__file__).resolve()))} --uninstall")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
