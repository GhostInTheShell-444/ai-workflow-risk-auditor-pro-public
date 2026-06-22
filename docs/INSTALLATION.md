# Installation

AI Workflow Risk Auditor Pro is a local Streamlit application. The deterministic audit requires no cloud account, API key, external database, or Ollama installation.

## Requirements

- Python 3.12
- Git
- A terminal with permission to create a virtual environment
- A current desktop browser

Use the private repository clone URL only if your GitHub account has access.

## Ubuntu and Debian Linux

Install Python, virtual-environment support, and Git if they are not already available:

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv git
```

Clone, create an isolated environment, and install dependencies:

```bash
git clone https://github.com/GhostInTheShell-444/ai-workflow-risk-auditor-pro.git
cd ai-workflow-risk-auditor-pro
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1
```

## macOS

Install Python 3.12 and Git using trusted packages appropriate for your environment. If Homebrew is already approved on your machine, one option is:

```bash
brew install python@3.12 git
```

Then:

```bash
git clone https://github.com/GhostInTheShell-444/ai-workflow-risk-auditor-pro.git
cd ai-workflow-risk-auditor-pro
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1
```

## Windows PowerShell

Install Python 3.12 and Git from trusted official installers, then open a new PowerShell window:

```powershell
git clone https://github.com/GhostInTheShell-444/ai-workflow-risk-auditor-pro.git
Set-Location ai-workflow-risk-auditor-pro
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1
```

## Open and stop the app

Open `http://127.0.0.1:8501` if Streamlit does not open a browser automatically. Keep the server bound to loopback. Stop it with `Ctrl+C`.

## Optional local Ollama

Ollama is optional. If it is not installed or enabled, all deterministic analysis, scoring, simulation, dashboard, knowledge-base, and report features remain available.

The app uses the local endpoint `http://localhost:11434`. Its client accepts only loopback hosts (`localhost`, `127.0.0.1`, or `::1`) and has no cloud fallback. After installing Ollama from its official distribution and installing a local model, start the local service according to the Ollama instructions. A typical local workflow is:

```bash
ollama serve
ollama pull llama3
```

Then enable **Use local Ollama enrichment** in the app. If Ollama is absent, leave the toggle disabled and ignore availability notices. Model output is wording assistance only and cannot change deterministic findings, scores, controls, or simulations.

## Local database and reset

The app creates `data/aiwra.db` on first run. This project-local SQLite database contains bundled seed records and reports you explicitly save. It is ignored by Git and is not encrypted by the app.

Preferred reset method:

1. Read the sidebar deletion warning.
2. Select the confirmation checkbox.
3. Select **Reset demo database**.

This deletes saved local reports and recreates synthetic seed data. Back up the database first if you need its contents.

Manual reset:

1. Stop Streamlit.
2. Back up `data/aiwra.db` if needed.
3. Delete only `data/aiwra.db`.
4. Restart the app so it recreates the database.

Do not delete `data/.gitkeep`.

## Troubleshooting

### Python is not found or is the wrong version

Run `python --version`, `python3.12 --version`, or `py -3.12 --version`. Install Python 3.12 and reopen the terminal. Use the explicit 3.12 launcher to create the environment.

### PowerShell blocks virtual-environment activation

Use a process-scoped policy for the current terminal, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Do not weaken machine-wide policy without administrator approval.

### Port 8501 is already in use

```bash
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502
```

Open `http://127.0.0.1:8502`.

### Dependency installation fails

Confirm the virtual environment is active and Python is 3.12, then retry:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If a corporate proxy or package mirror is required, follow your organization's approved package-management process. Do not put credentials in repository files or terminal transcripts.

### Streamlit does not open

Use `python -m streamlit` instead of the bare `streamlit` command, confirm the terminal shows a local URL, and open `http://127.0.0.1:8501` manually. Check local firewall/browser restrictions without binding the server to a public interface.

### Ollama is unavailable

Leave the Ollama toggle disabled. If local AI is intentionally required, confirm the local service responds at `http://localhost:11434`, a local model is installed, and no remote endpoint is configured. Deterministic auditing does not depend on it.

### Screenshots do not appear in the GitHub README

Confirm the PNG exists with the same case-sensitive path, is tracked in the same branch, and uses repository-relative Markdown such as `![Description](screenshots/01_home_audit.png)`. See [Screenshot Guidelines](SCREENSHOT_GUIDELINES.md).

### GitHub CLI is not authenticated

```bash
gh auth login -h github.com -p https -w
gh auth status -h github.com
```

Never paste access tokens into issue text, documentation, shared command output, or AI prompts. See [GitHub Repository Setup](GITHUB_REPOSITORY_SETUP.md).

Continue with the [Usage Guide](USAGE.md).
