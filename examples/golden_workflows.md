# Golden Synthetic Workflows

These examples are fictional and safe for local manual testing.

## Low-risk reviewed drafting

```text
AI drafts an internal summary from synthetic project notes.
A named human reviewer approves the summary.
No external message or production action occurs.
```

## High-risk automatic refund approval

```text
AI automatically approves and issues customer refunds from synthetic billing records.
There is no human review, audit log, appeal, masking, retention, or fallback.
```

## Sensitive customer support

```text
AI summarizes synthetic customer tickets containing email addresses and billing context.
The workflow does not define masking, minimization, or retention.
```

## Local-only Ollama reviewer

```text
Ollama runs as local-only AI on localhost with no cloud fallback.
It drafts reviewer questions from synthetic workflow text.
A human owns every decision.
```

## Missing retention and appeal

```text
AI ranks synthetic applicants and recommends rejection.
The workflow does not define retention, appeal, recourse, or manual exception review.
```

## Human fallback

```text
AI drafts a customer response from redacted synthetic notes.
A named support reviewer approves it before sending.
Failures enter a manual queue, retries are limited, the event is logged, and rollback is documented.
```

## French smoke

```text
Le système IA rédige une réponse à partir de données clients synthétiques.
Un reviewer humain nommé valide le message, un journal d'audit est conservé et les échecs passent dans une file manuelle.
```

## Hebrew RTL smoke

```text
מערכת AI מנסחת תשובה מתוך נתוני דמו סינתטיים.
בודק אנושי מאשר לפני שליחה, נשמר לוג ביקורת, ובמקרה כשל העבודה עוברת לתור ידני.
```
