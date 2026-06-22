# GitHub Repository Setup

These are human-run administration instructions for the official public repository. Repository visibility changes require separate owner authorization and are outside this setup guide.

## Authenticate GitHub CLI safely

Use the browser-based login flow:

```bash
gh auth login -h github.com -p https -w
gh auth status -h github.com
```

Do not paste access tokens into AI prompts, issues, pull requests, documentation, screenshots, or shared logs. Do not run `gh auth token` in shared logs.

GitHub CLI normally stores credentials in the operating system's credential store. If no supported credential store is available, it may fall back to storing a token in a plain-text configuration file. Review the authentication output and local security posture before proceeding.

## Verify public repository identity and visibility

Read-only check:

```bash
gh repo view GhostInTheShell-444/ai-workflow-risk-auditor-pro-public --json nameWithOwner,visibility,isPrivate,url
```

Expected: `nameWithOwner` is `GhostInTheShell-444/ai-workflow-risk-auditor-pro-public`, `visibility` is `PUBLIC`, `isPrivate` is `false`, and the URL identifies that same repository. If any field differs, stop repository administration and have the owner investigate.

Do not change repository visibility as part of routine setup or publication.

Any legacy repository must remain private and must not be linked or described as the official public repository.

## Verify clean publication state

Use read-only checks to confirm that contributors, pull requests, releases, tags, workflow runs, and remote refs match the intended publication state. The active repository should contain `.github/dependabot.yml.disabled` and must not contain an active `.github/dependabot.yml` while automated dependency pull requests are intentionally disabled for the clean public launch.

The initial public state intentionally has no release or tag. Do not create either without a separate owner-approved release decision.

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
- branch protection or repository rules match the maintainer workflow.

## Recommended `Protect main` ruleset

If no branch ruleset exists, an owner can create one manually in **Settings → Rules → Rulesets** after reviewing the effects and available bypass controls:

- name the ruleset `Protect main`;
- set enforcement to **Active**;
- target the default branch or `main`;
- restrict branch deletions;
- block force pushes;
- require linear history;
- leave **Restrict updates** disabled unless the owner has verified an appropriate bypass path;
- do not require pull-request approvals for a solo-maintainer workflow unless the owner chooses that process;
- require status checks only when the `CI` check is selectable and the owner approves making it mandatory.

After saving, verify the ruleset with a read-only API request or in the GitHub UI. Do not edit rulesets during a documentation or publication audit.

Do not create a tag or release as part of repository setup. Those require a separate human-approved release decision.
