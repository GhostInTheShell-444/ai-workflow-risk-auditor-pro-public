# Score Explainability

## One-Minute Explanation

This tool reads a workflow, detects risk clues, calculates a local rule-based risk score, explains why, recommends protections, and simulates the remaining risk. It does not certify compliance and does not replace human judgment.

## What The Score Measures

The main displayed score is the raw risk matrix score.

It measures how many local risk factors were mapped from:

- evidence detected in the submitted workflow text;
- compatibility factors detected by the original deterministic analyzer.

It does not measure the true probability of harm.

## How The Score Is Calculated

The score is deterministic:

```text
raw matrix score = sum of mapped local risk-factor weights
```

Severity thresholds:

- 0-4 = Low
- 5-9 = Medium
- 10-15 = High
- 16+ = Critical

The app may also show a compatibility score. That score comes from the original analyzer and is preserved for backward compatibility.

## What Makes A Finding Explainable

Each important finding should show:

- the evidence text;
- the local rule id;
- severity;
- confidence;
- mapped risk factors;
- recommended controls;
- whether the statement is detected, calculated, simulated, recommended, or uncertain.

## What The Numbers Do Not Mean

- They are not statistical probabilities.
- They are not calibrated risk predictions.
- They are not legal advice.
- They are not compliance certification.
- They are not approval to automate.

This score is a rule-based estimate, not a statistical probability. Score calculated from local deterministic rules. It is an aid, not a certification.

## Why Human Review Remains Required

The app can detect clues, but it cannot know all business context, legal duties, customer commitments, or production constraints. A responsible human must decide whether the evidence is relevant and whether a workflow should be automated.
