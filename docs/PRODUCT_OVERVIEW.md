# Product Overview

## What the system is

AI Workflow Risk Auditor Pro is a local-first Streamlit application for reviewing proposed AI-assisted workflows before production integration. It turns synthetic or anonymized workflow text into step-level evidence, deterministic risk indicators, recommended controls, human validation checkpoints, residual-risk simulations, and exportable reports.

## Why it exists

Workflow automation decisions often move faster than security, privacy, governance, and operational review. A team may understand the intended benefit without having a shared way to explain what data is involved, which steps are risky, why a score changed, or where human approval belongs. This project provides a transparent discussion aid without requiring a cloud service.

## Who it is for

- Security and privacy practitioners reviewing designs.
- AI governance, risk, audit, and assurance teams.
- Product managers and architects planning AI-assisted processes.
- Developers who need inspectable local rules and reproducible tests.
- Educators, portfolio reviewers, and teams running synthetic workshops.

## Why it matters in 2026

AI is increasingly embedded in business workflows rather than used only as a standalone chat interface. This creates combined risks involving sensitive data, external actions, human oversight, auditability, and model-assisted decisions. Reviewers need tools that keep early-stage workflow material local, show their reasoning, and make limitations obvious.

## Core features

The application provides workflow input and synthetic scenarios, a deterministic analyzer, evidence and sensitive-data detection, cybersecurity/privacy risk detection, a risk matrix, score explainability, top risks and actions, control recommendations, human validation planning, residual-risk simulation, Markdown/JSON exports, explicit-save SQLite history, a visual dashboard, a searchable local Knowledge Base, EN/FR/HE interfaces, Hebrew RTL support, theme selection, and optional localhost-only Ollama narrative assistance.

## How the score is calculated

Local patterns detect evidence within extracted workflow steps. Evidence maps to named risk factors. Each known factor has a fixed local weight; normalized unique factor weights are summed deterministically. Fixed thresholds map totals to low, medium, high, or critical review priority. The matrix also exposes evidence-derived likelihood, weight-derived impact, deterministic confidence, and per-factor score impact.

The UI distinguishes the analyzer compatibility score from the raw evidence-based matrix score. The calculation path is inspectable in source code, report output, and the score basis view.

## What the score does not mean

Scores are rule-based estimates, not statistical probabilities. They are not calibrated loss estimates, facts about production behavior, compliance results, legal advice, security approval, or permission to automate. A finding indicates matched text or a local pattern; a human must decide whether it is relevant.

This is not a certification.

## What stays local

Deterministic analysis, knowledge files, score calculations, simulations, report rendering, and the SQLite database are local. User workflow text is held in Streamlit session state during use and written to the project-local database only after an explicit save action. Downloads do not require saving. No telemetry, cloud API, external database, or vendor key is required.

## What Ollama adds

Optional Ollama support can run a synthetic diagnostic and generate narrative wording for the current report. It shows the text sent and the local response. The client accepts only loopback endpoints and only models listed as local by the localhost Ollama service.

## What Ollama does not do

Ollama does not create rules, detect hidden findings, change scores, validate calculations, select or implement controls, change residual-risk simulation, certify compliance, or provide a cloud fallback. The application remains functional when Ollama is absent.

## What is simulated

Residual risk and score reduction are simulated from predefined mappings between selected controls and risk factors. The simulation does not verify implementation, measure operational effectiveness, execute remediation, or guarantee production risk reduction.

## What is recommended

Controls, next actions, human checkpoints, and local follow-up items are advisory outputs derived from matched rules. They must be evaluated by appropriate owners. The control checklist does not prove that a control exists or works.

## What requires human review

Humans must validate the workflow description, finding relevance, source evidence, risk assumptions, regulatory context, control applicability, residual-risk assumptions, translations, and any decision to connect the workflow to production. External, people-affecting, irreversible, or high-impact actions require explicit governance outside this tool.

## Limitations

Keyword and regular-expression matching can miss context and produce false positives. Deterministic confidence is heuristic. The knowledge base is finite and not a complete threat or compliance catalog. Translation parity does not replace professional language review. System theme currently resolves to light. Optional Ollama output can be inaccurate and is wording assistance only. The app does not inspect or connect to live systems.

## How to demo it

Use a synthetic scenario, run the audit, open the evidence and calculation basis, simulate selected controls, download both report formats, then explicitly save once to demonstrate local history. Show the dashboard, Knowledge Base, French and Hebrew interfaces, and the Local AI boundary. Keep Ollama optional and state the score and simulation limitations aloud.

See [Public Demo Guide](PUBLIC_DEMO_GUIDE.md) and [Screenshot Specification](SCREENSHOTS_TODO.md).
