# GitHub Repository Setup

These are human-run administration instructions for the official public repository. Repository visibility changes require separate owner authorization and are outside this setup guide.

## Authenticate GitHub CLI safely

Use the browser-based login flow:

```bash
gh auth login -h github.com -p https -w
gh auth status -h github.com
```

Do not paste access tokens into Codex, AI prompts, issues, pull requests, documentation, screenshots, or shared logs. Do not run `gh auth token` in shared logs.

GitHub CLI normally stores credentials in the operating system's credential store. If no supported credential store is available, it may fall back to storing a token in a plain-text configuration file. Review the authentication output and local security posture before proceeding.

## Verify public repository identity and visibility

Read-only check:

```bash
gh repo view GhostInTheShell-444/ai-workflow-risk-auditor-pro-public --json nameWithOwner,visibility,isPrivate,url
```

Expected: `nameWithOwner` is `GhostInTheShell-444/ai-workflow-risk-auditor-pro-public`, `visibility` is `PUBLIC`, `isPrivate` is `false`, and the URL identifies that same repository. If any field differs, stop repository administration and have the owner investigate.

Do not change repository visibility as part of routine setup or publication.

## About section

Recommended description:

> Local-first Streamlit tool to explain, score, simulate, and document AI workflow risks before automation.

Leave the homepage blank unless a reviewed public URL exists. Do not add a localhost, private deployment, tracking, or temporary preview URL.

## Recommended topics

Add and review these topics in the GitHub repository About settings:

```text
python
streamlit
cybersecurity
ai-governance
local-first
privacy
risk-assessment
sqlite
ollama
explainability
ai-safety
workflow-automation
security-audit
governance
compliance
```

## Social preview

Prepare a 1280×640 image that:

- uses the project title and concise local-first positioning;
- contains only synthetic product data;
- avoids terminals, browser chrome, private tabs, and notification overlays;
- contains no local paths, emails, machine names, credentials, or tokens;
- contains no real report history, organization names, or personal notes;
- remains readable at small card sizes.

Have another person complete a privacy/visual review before upload.

## Manual GitHub settings review

In the GitHub UI, verify:

- the default branch is `main`;
- the About description is exact and topics are present;
- Actions have least-privilege read-only contents permission where possible;
- issue forms and pull-request template render correctly;
- private vulnerability reporting is enabled for the public repository;
- README images render with meaningful alt text;
- the restrictive source-available, non-commercial terms in `LICENSE`, `NOTICE.md`, and `LICENSING_AND_COMMERCIAL_USE.md` remain consistent;
- branch protection and required CI checks match the maintainer workflow.

Do not create a tag or release as part of repository setup. Those require a separate human-approved release decision.
