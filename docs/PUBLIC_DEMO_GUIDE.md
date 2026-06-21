# Public Demo Guide

Use this flow for a recruiter, manager, auditor, or security professional.

## Setup

Run locally:

```bash
streamlit run app.py --server.address 127.0.0.1
```

Use a synthetic example. Do not paste real sensitive data.

## Five-Minute Demo

1. Open the app.
2. Show the one-minute explanation and simple legend.
3. Choose the Customer Support example.
4. Run the audit.
5. Point to the score and explain that it is calculated from local deterministic rules.
6. Open the top risk evidence and rule id.
7. Open calculation basis.
8. Go to Simulation and simulate selected protections.
9. Explain residual risk as simulated, not guaranteed.
10. Download Markdown and JSON.
11. Open Dashboard only after saving a report locally.

## Talk Track

This is a local-first proof of concept for understanding AI workflow risk before production integration. It does not certify compliance, does not connect to production systems, and does not send workflow text to a cloud API.

## What To Avoid Claiming

- Do not claim the score is scientifically true.
- Do not claim the tool certifies compliance.
- Do not claim residual risk is guaranteed.
- Do not claim the app replaces an auditor or security reviewer.
