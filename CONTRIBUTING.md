# Contributing

Contributions should preserve the project's deterministic, explainable, local-first behavior.

## Local setup

Python 3.12 is the supported development version. See [Installation](docs/INSTALLATION.md) for Linux, macOS, and Windows commands.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py --server.address 127.0.0.1
```

Use synthetic or anonymized inputs. Ollama is optional and must not be required to develop or test deterministic features.

## Validation

Run before opening a pull request:

```bash
python -m pytest
python -m compileall app.py analyzer.py database.py repositories.py workflow_parser.py report_renderer.py export_json.py score_explainability.py design_tokens.py ui_components.py tests locales
```

New features and bug fixes require focused tests. UI changes require a manual check in Light and Dark themes and, where relevant, French and Hebrew RTL.

Documentation-only changes must pass `git diff --check`, preserve valid relative links, and use names and paths that exist in the repository.

## Code expectations

- Keep domain logic testable outside Streamlit where practical.
- Preserve deterministic score inputs, fixed mappings, and source/meaning/limit explanations.
- Make simulation and recommendation language explicit; never imply a control was implemented.
- Prefer small modules, typed data structures where useful, clear names, and no hidden network behavior.
- Update public docs, sample output, and limitations when behavior changes.

## Privacy and local-first rules

- Do not add cloud APIs, telemetry, external databases, SaaS behavior, or remote model fallbacks without explicit public design discussion and security review.
- Do not transmit workflow text outside loopback by default.
- Keep persistence explicit; analysis must not silently save user input.
- Do not commit databases, virtual environments, caches, bytecode, logs, environment files, Streamlit secrets, credentials, or personal data.
- Do not place real workflow content in tests, issues, screenshots, fixtures, or reports.

## Internationalization

Every new visible UI string must be represented in English, French, and Hebrew locale files. Preserve locale key parity, English fallback behavior, and Hebrew RTL layout. Technical identifiers, code, JSON, endpoints, and model names may remain LTR.

## Documentation, examples, and screenshots

- Keep examples entirely synthetic; never paste real workflow, organization, account, or report data.
- Use `DEMO_ONLY`, `REDACTED`, or `EXAMPLE_NOT_A_SECRET` for placeholders that could otherwise look sensitive.
- Follow [Screenshot Guidelines](docs/SCREENSHOT_GUIDELINES.md) and inspect every image at full size.
- Place French and Hebrew RTL captures in the internationalization gallery rather than the primary English flow.
- Update README and detailed docs together when behavior or limitations change.

## Pull requests

Describe the use case, deterministic scoring impact, local-first impact, security/privacy impact, localization impact, tests, documentation, and manual visual checks. Keep pull requests focused and avoid unrelated generated artifacts.
