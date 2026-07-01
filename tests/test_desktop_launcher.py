from __future__ import annotations

from pathlib import Path

from scripts.install_desktop_launcher import (
    APP_ID,
    APP_NAME,
    build_desktop_entry,
    remove_launcher,
    write_launcher,
)


ROOT = Path(__file__).resolve().parents[1]


def test_desktop_entry_is_local_only_and_handles_spaces(tmp_path):
    project = tmp_path / "AIWRA project with spaces"
    project.mkdir()
    content = build_desktop_entry(project)

    assert f"Name={APP_NAME}" in content
    assert f'Exec="{project.resolve()}/scripts/launch_aiwra.sh"' in content
    assert f"Icon={project.resolve()}/assets/aiwra_icon.svg" in content
    assert f"Path={project.resolve()}" in content
    assert "Terminal=false" in content
    assert "sudo" not in content.casefold()
    assert "/usr/share/applications" not in content


def test_launcher_write_is_idempotent_and_removable(tmp_path):
    destination = tmp_path / "applications" / APP_ID
    content = build_desktop_entry(tmp_path / "project")

    assert write_launcher(destination, content) is True
    assert write_launcher(destination, content) is False
    assert destination.read_text(encoding="utf-8") == content
    assert destination.stat().st_mode & 0o111
    assert remove_launcher(destination) is True
    assert remove_launcher(destination) is False


def test_launch_helpers_use_loopback_without_privilege_escalation():
    linux = (ROOT / "scripts" / "launch_aiwra.sh").read_text(encoding="utf-8")
    windows = (ROOT / "scripts" / "create_windows_shortcut.ps1").read_text(encoding="utf-8")
    macos = (ROOT / "scripts" / "create_macos_launcher.sh").read_text(encoding="utf-8")

    for content in (linux, windows, macos):
        assert "127.0.0.1" in content
        assert "8501" in content
        assert "0.0.0.0" not in content
        assert "sudo" not in content.casefold()
        assert "systemctl" not in content.casefold()
        assert "/etc/systemd" not in content.casefold()
    assert "--server.address 127.0.0.1" in linux
    assert "AIWRA_PORT must be between 1 and 65535." in linux
    assert 'Project: $PROJECT_DIR' not in linux
    assert ".venv/bin/python" in linux
    assert "Port must be between 1 and 65535." in windows
    assert ".venv\\Scripts\\python.exe" in windows


def test_local_svg_icon_is_safe_and_self_contained():
    icon = ROOT / "assets" / "aiwra_icon.svg"
    text = icon.read_text(encoding="utf-8")

    assert icon.stat().st_size > 100
    assert "<svg" in text
    assert "<script" not in text.casefold()
    assert "https://" not in text.casefold()
    assert "href=" not in text.casefold()
    assert text.casefold().count("http://") == 1
    assert "http://www.w3.org/2000/svg" in text
