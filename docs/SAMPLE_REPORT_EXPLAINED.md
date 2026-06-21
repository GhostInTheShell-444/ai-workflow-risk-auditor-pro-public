# Sample Report Explained

This page explains the synthetic Customer Support example in simple terms.

## Input

The workflow says a support team receives anonymized customer emails, lets AI draft responses, requires support-agent review, escalates complex complaints, and keeps an audit log.

## Detected

The tool detected:

- customer support text;
- customer emails and support tickets;
- possible customer-facing responses;
- policy exceptions;
- audit log and review language.

## Calculated

Current output from the code:

- Compatibility score: 10, High.
- Raw matrix score: 17, Critical.
- Findings: 35.

Plain meaning:

The workflow has useful safeguards, but the text still mentions customer data, external communication, policy exceptions, and other signals that local rules treat as high attention.

## Simulated

With default selected controls:

- Raw score: 17.
- Simulated residual score: 9.
- Simulated reduction: 8.

This is a planning estimate, not a guarantee.

## Recommended

Top actions include:

- require human approval before external messages;
- keep an audit trail;
- minimize data;
- show confidence labels;
- keep recommendation separate from execution.

## Human Responsibility

A support lead, privacy reviewer, or security reviewer must decide whether the evidence is relevant and whether the controls are enough.
