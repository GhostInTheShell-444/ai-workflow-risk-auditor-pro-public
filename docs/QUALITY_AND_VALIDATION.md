# Quality and Validation

The project documents reproducible checks that visitors and contributors can run locally.

## Automated coverage

The test suite covers deterministic analysis, evidence and rules, risk matrices, controls, residual-risk simulation, SQLite persistence, report exports, localization parity, Hebrew RTL report rendering, UI data helpers, theme tokens, knowledge files, and optional-Ollama endpoint/model guardrails.

Run the same core checks used by contributors:

```bash
python -m pytest
python -m compileall app.py analyzer.py database.py repositories.py workflow_parser.py report_renderer.py export_json.py score_explainability.py design_tokens.py ui_components.py tests locales
```

Tests require no Ollama service, cloud API, secret, network account, or existing database. CI configuration is available in `.github/workflows/ci.yml`.

## Human validation still required

Automated tests do not establish browser rendering quality, translation quality, accessibility conformance, production security, regulatory compliance, or real-world control effectiveness. Light, Dark, French, and Hebrew RTL presentation and all public screenshots require human inspection. Findings, score assumptions, proposed controls, and simulated reductions also require context-specific review.

See [Score Explainability](SCORE_EXPLAINABILITY.md), [Privacy Model](PRIVACY_MODEL.md), [Security Audit](SECURITY_AUDIT.md), and the [Public Screenshot Specification](SCREENSHOTS_TODO.md).
