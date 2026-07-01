# Optional Desktop Launcher

The desktop launcher is a convenience layer for the local Streamlit application. It does not package the project, install a system service, require a cloud account, or change the risk engine.

All provided launchers bind Streamlit to `127.0.0.1` on port `8501` by default. They require an existing project-local `.venv` with Streamlit installed. No launcher stores credentials or uses `sudo`.

## Linux: supported first

From the project directory:

```bash
.venv/bin/python scripts/install_desktop_launcher.py
```

The installer validates:

- the project directory and `app.py`;
- `scripts/launch_aiwra.sh`;
- the local SVG icon;
- `.venv/bin/python`;
- the ability to import Streamlit from that environment.

It creates or replaces:

```text
~/.local/share/applications/ai-workflow-risk-auditor-pro.desktop
```

The write is idempotent. Running the installer again updates the same launcher.

To also create a desktop shortcut when `~/Desktop` exists:

```bash
.venv/bin/python scripts/install_desktop_launcher.py --desktop
```

To keep a terminal visible during startup:

```bash
.venv/bin/python scripts/install_desktop_launcher.py --terminal
```

The launch helper opens the browser with `xdg-open` when available and records Streamlit output at:

```text
${XDG_STATE_HOME:-$HOME/.local/state}/aiwra/aiwra-launch.log
```

The helper does not intentionally write the project path or workflow content to this log. Streamlit and dependency diagnostics may still contain local environment details. Treat launcher logs as private runtime artifacts: review them before sharing and remove them when no longer needed.

Override the port for a single terminal launch:

```bash
AIWRA_PORT=8502 scripts/launch_aiwra.sh
```

The address remains fixed to `127.0.0.1`.

### Remove the Linux launcher

```bash
.venv/bin/python scripts/install_desktop_launcher.py --uninstall
```

This removes only the expected user-local application and desktop shortcut paths. It does not remove the project, virtual environment, database, reports, or logs.

## Windows PowerShell

After creating `.venv` and installing requirements, run from PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create_windows_shortcut.ps1
```

The script creates `AI Workflow Risk Auditor Pro.lnk` on the current user’s desktop. The shortcut opens PowerShell in the project directory and runs:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

No administrator rights are required. Remove it with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create_windows_shortcut.ps1 -Remove
```

The canonical icon is SVG. Windows shortcut icon rendering usually requires `.ico`, so the helper does not claim native icon integration.

## macOS

After creating `.venv` and installing requirements:

```bash
scripts/create_macos_launcher.sh
```

This creates:

```text
~/Desktop/AI Workflow Risk Auditor Pro.command
```

The generated command launches Streamlit on `127.0.0.1:8501`, opens the local browser URL, and writes logs to:

```text
~/Library/Logs/AIWRA/aiwra-launch.log
```

Treat this log as a private runtime artifact and review it before sharing.

No administrator rights are required. Delete the generated `.command` file to remove it. This helper is provided and statically reviewed but was not tested on macOS during this Linux implementation pass.

## Troubleshooting

If the launcher exits immediately:

1. Run the platform helper from a terminal to read its validation message.
2. Confirm `.venv` exists and belongs to this project.
3. Run `.venv/bin/python -c "import streamlit"` on Linux/macOS or `.\.venv\Scripts\python.exe -c "import streamlit"` on Windows.
4. Review the platform log.
5. Confirm port `8501` is free, or use the documented Linux port override.

Do not solve port or browser issues by binding Streamlit to `0.0.0.0`. The desktop path is intentionally localhost-only.
