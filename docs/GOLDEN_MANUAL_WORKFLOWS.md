# Golden Manual Workflows

Use only these synthetic examples for manual checks and screenshots. They contain no real people, customers, accounts, credentials, or production data.

1. **Low-risk reviewed drafting**

   `AI drafts an internal summary from synthetic project notes. A named human reviewer approves the summary. No external message or production action occurs.`

2. **High-risk automatic refund approval**

   `AI automatically approves and issues customer refunds from synthetic billing records without human review, audit logs, appeal, masking, or fallback.`

3. **Sensitive-data customer support**

   `AI summarizes synthetic customer support tickets containing email addresses and billing context. The description does not specify masking or retention.`

4. **Local-only Ollama reviewer**

   `Ollama runs as local-only AI on localhost with no cloud fallback. It drafts reviewer questions from synthetic workflow text. A human owns every decision.`

5. **Missing retention and appeal**

   `AI ranks synthetic applicants and recommends rejection. The workflow does not define retention, appeal, recourse, or manual exception review.`

6. **Human fallback workflow**

   `AI drafts a customer response. A named support reviewer approves it. Failures enter a manual queue, retries are limited, the event is logged, and a rollback path is documented.`

7. **French UI smoke**

   `Le système IA rédige une réponse à partir de données clients synthétiques. Un reviewer humain nommé valide le message, un journal d’audit est conservé et les échecs passent dans une file manuelle.`

8. **Hebrew RTL smoke**

   `מערכת AI מנסחת תשובה מתוך נתוני דמו סינתטיים. בודק אנושי מאשר לפני שליחה, נשמר לוג ביקורת, ובמקרה כשל העבודה עוברת לתור ידני.`

## Manual expectations

- Automatic refund approval scores higher than reviewed drafting.
- Missing masking, retention, appeal, audit, approval, and fallback produce explicit gap findings.
- Audit and fallback wording are contextual evidence and do not prove implementation.
- Local-only Ollama wording does not create cloud dependency.
- French and Hebrew presentation changes do not alter deterministic output.
- Hebrew remains RTL while JSON, model names, endpoints, and rule IDs remain readable LTR.
