# Score Calculation Trace

This document traces the implemented calculation path. It does not define a separate scoring model.

## Source Files

| Area | Responsible module/function | Inputs used | Output produced |
| --- | --- | --- | --- |
| Input cleanup | `analyzer.clean_input`, `workflow_parser.clean_workflow_text` | User-pasted workflow text | Normalized local text |
| Workflow steps | `analyzer.extract_steps`, `workflow_parser.extract_workflow_steps` | Cleaned text | Step list |
| Workflow type | `analyzer.classify_workflow` | Keyword hits in cleaned text | Workflow type such as `customer_support`, `hr`, `soc`, `logistics` |
| Sensitive data categories | `analyzer.detect_sensitive_data` | Local keyword map in `analyzer.py` | Category keys such as `customer_data` |
| Compatibility factors | `analyzer.detect_risk_factors` | Text signals, categories, review/audit keywords | Original deterministic factor list |
| Compatibility score | `risk_rules.calculate_risk` | Compatibility factors | `risk.score`, `risk.level`, factor breakdown |
| Evidence findings | `evidence_engine.run_evidence_engine` | Parsed steps, `knowledge_base/risk_patterns.json` | Findings with evidence, rule id, severity, confidence, controls, mapped factors |
| Raw risk matrix | `risk_matrix.calculate_risk_matrix` | Findings and compatibility factors | `raw_risk_score`, severity, likelihood, impact, confidence, entries |
| Recommended controls | `controls_engine.recommend_controls` | Finding `recommended_controls` ids | Control list from `knowledge_base/control_library.json` |
| Residual risk | `residual_risk.simulate_residual_risk` | Raw matrix entries and selected controls | Simulated residual score, reduction, remaining risks |
| Markdown report | `report_renderer.render_markdown_report` | Analysis, optional simulation, optional local enrichment | Markdown report |
| JSON export | `export_json.build_json_summary` | Analysis, optional simulation | JSON-compatible dict |
| Dashboard metrics | `repositories.get_dashboard_metrics` | Saved local SQLite rows | Counts, averages, distributions, latest reports |
| Locales / RTL | `i18n.t`, `i18n.is_rtl`, `locales/*.json` | Language code | UI/report labels and Hebrew direction |

## Score Rules And Weights

The compatibility score uses `risk_rules.RISK_FACTORS`. The score is the sum of weights for normalized factor keys.

Important weights:

| Factor | Weight |
| --- | ---: |
| `personal_data` | 2 |
| `customer_data` | 2 |
| `hr_candidate_data` | 3 |
| `financial_data` | 3 |
| `medical_health_data` | 4 |
| `legal_compliance_data` | 3 |
| `external_communication` | 2 |
| `customer_facing_automated_output` | 3 |
| `decision_affecting_person` | 4 |
| `irreversible_action` | 4 |
| `data_modification_deletion` | 4 |
| `third_party_integration` | 2 |
| `sensitive_system_access` | 3 |
| `missing_human_validation` | 3 |
| `missing_audit_trail` | 2 |
| `broad_ai_agent_permissions` | 4 |
| `soc_security_workflow` | 3 |
| `credentials_secrets` | 4 |
| `prompt_injection_exposure` | 2 |

Severity thresholds are fixed in `risk_rules.get_risk_level`:

- 0-4: low
- 5-9: medium
- 10-15: high
- 16+: critical

## Raw Risk Matrix

`risk_matrix.calculate_risk_matrix` builds a factor count from findings and compatibility factors.

- Raw matrix score = sum of mapped local factor weights.
- Likelihood = derived from evidence count for each factor, capped from 1 to 5.
- Impact = derived from factor weight.
- Confidence = average finding confidence for that factor.
- Severity = fixed thresholds from `risk_rules.get_risk_level`.

This score is a rule-based estimate, not a statistical probability.

## Controls And Residual Risk

`controls_engine.recommend_controls` maps findings to controls by id.

`residual_risk.simulate_residual_risk` then:

1. Starts with each risk-matrix factor score.
2. Reads selected controls from `knowledge_base/control_library.json`.
3. Applies `reduced_risk_factors` amounts only to factors present in the matrix.
4. Floors each factor score at zero.
5. Sums remaining factor scores.

Residual risk is simulated. It does not execute actions and does not guarantee production risk reduction.

## Customer Support Example

Synthetic input:

```text
A customer support inbox receives anonymized customer emails and support tickets.
An AI workflow may draft a suggested answer.
A support agent reviews the draft before sending.
Complex complaints, refunds, or policy exceptions are escalated.
The process keeps an audit log.
```

Observed output from the current code:

- Compatibility score: 10, High.
- Raw matrix score: 17, Critical.
- Findings: 35.
- Simulated residual score with default selected controls: 9.
- Simulated reduction: 8.

Plain reading:

The workflow mentions customer support, external messages, customer context, policy exceptions, and audit/review steps. Local rules detect risk clues and also detect some protections. The raw score is high enough to require human review before automation. The residual score is only a simulation after selected controls.

## Limitations

- Keyword and regex rules can produce false positives.
- Keyword and regex rules can miss context.
- Scores are not calibrated probabilities.
- Scores are useful for orientation, not certification.
- Findings show detected evidence and rule matches; they still require human review.
- Residual risk is a planning simulation, not operational assurance.
