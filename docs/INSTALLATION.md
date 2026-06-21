# Installation

AI Workflow Risk Auditor Pro runs as a local Streamlit application. The deterministic audit does not require Ollama, a cloud API, an API key, or an external database.

## Prerequisites

- Python 3.12
- Git
- A terminal with permission to create a virtual environment

## Clone and install

Replace `<REPOSITORY_URL>` with the GitHub clone URL:

```bash
git clone <REPOSITORY_URL> ai-workflow-risk-auditor-pro
cd ai-workflow-risk-auditor-pro
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Run

```bash
streamlit run app.py --server.address 127.0.0.1
```

Open `http://127.0.0.1:8501` if Streamlit does not open a browser automatically. Stop the server with `Ctrl+C`.

## Local data

The app creates `data/aiwra.db` on first run. This project-local SQLite file stores only bundled seed content and reports that you explicitly save. Running an audit or downloading a report does not add it to saved history. The database is ignored by Git and is not encrypted by the app.

To reset from the UI, use the sidebar confirmation and **Reset demo database** control. This deletes saved local reports and recreates synthetic seed data.

To remove all local app data manually, stop Streamlit, back up `data/aiwra.db` if needed, then delete only that file. The app recreates it on the next launch. Do not delete the `data/` directory or its `.gitkeep` file.

## Troubleshooting

- If `streamlit` is not found, confirm the virtual environment is active or run `python -m streamlit run app.py --server.address 127.0.0.1`.
- If port 8501 is in use, add `--server.port 8502` and open `http://127.0.0.1:8502`.
- If installation fails, confirm `python --version` reports Python 3.12 and update the environment installer with `python -m pip install --upgrade pip`.
- Ollama warnings do not prevent deterministic audits. Leave Ollama disabled unless you intentionally want local narrative assistance.

Continue with the [Usage Guide](USAGE.md).
