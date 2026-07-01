# Public Release Checklist

Use this checklist for public-repository verification and future republishes. Privacy, secret, identity, licensing, history, and test failures are blockers; presentation improvements may remain tracked as non-blocking work.

This checklist is a future human gate, not a publication authorization. The current local working tree remains non-committable, non-pushable, and non-publishable until a separate final QA/publication-readiness review is completed.

## P0 — blockers

- [ ] Complete a final human privacy review of every screenshot.
- [ ] Verify the official public repository identity and visibility.
- [x] Include the intended restrictive source-available, non-commercial license.
- [ ] Render and review the README as an external visitor would see it.
- [ ] Test installation on Ubuntu/Debian Linux.
- [ ] Test installation on macOS.
- [ ] Test installation on Windows PowerShell.
- [ ] Confirm GitHub Actions is green for the final commit after the final push.
- [ ] Scan tracked and proposed files for real email addresses, local paths, machine names, and personal notes.
- [ ] Scan tracked and proposed files for credentials, secrets, tokens, cookies, and environment values.
- [ ] Confirm no private review reports or internal instruction files are tracked or linked.
- [ ] Confirm no runtime database, virtual environment, cache, bytecode, log, environment file, or Streamlit secrets file is tracked.
- [x] Set the GitHub About description to the approved one-sentence description; recheck during publication verification.
- [ ] Set and review repository topics.
- [ ] Add and privacy-review a 1280×640 social preview.
- [ ] Run final link, image-path, Markdown, test, and localhost smoke checks.
- [ ] Record the publication verification result and responsible owner.
- [ ] Confirm the public contributor list contains only the intended maintainer identity.
- [ ] Confirm pull requests, releases, and tags are empty for the initial publication state.
- [ ] Confirm remote refs contain only `HEAD` and `refs/heads/main`.
- [ ] Confirm `.github/dependabot.yml` is absent and `.github/dependabot.yml.disabled` is present while automated dependency pull requests remain intentionally disabled.
- [ ] Confirm any legacy repository remains private and is not presented as the official public repository.
- [ ] Verify the `Protect main` ruleset, or record the missing ruleset as manual follow-up.

## P1 — quality

- [ ] Recapture the dashboard with meaningful metrics/widgets visible.
- [ ] Recapture Local AI / Ollama with tab-specific status, safeguards, or synthetic output visible.
- [ ] Recapture Reports with a synthetic Markdown/JSON preview and export controls visible.
- [ ] Recapture Knowledge Base with rules, controls, or categories visible.
- [ ] Remove or hide the Streamlit **Deploy** control from public-polish captures if feasible.
- [ ] Review FAQ wording and answers.
- [ ] Run a documentation link/path check.
- [ ] Review every synthetic example for privacy and clarity.
- [ ] Review the roadmap for accurate commitments and non-goals.
- [ ] Perform French wording review.
- [ ] Perform Hebrew wording and RTL review.

## Publication verification record

- Approval owner:
- Approval date:
- Approved commit:
- Final CI run:
- Screenshot review completed by:
- License confirmed by:
- Repository identity verified by:

Maintainers may complete this record for a specific publication review without committing private operational details.

## Verified state on 2026-06-23 before local upgrade commit

- Public repository visibility: public.
- Legacy repository visibility: private.
- Contributor API result: only `GhostInTheShell-444`.
- Pull requests, releases, and tags: empty.
- Remote refs: `HEAD` and `refs/heads/main` only.
- Latest visible CI runs: passing.
- Ruleset: `Protect main`, active, branch target.
- Dependabot remains intentionally disabled for the clean launch.
- No release, tag, or package exists.

These facts were checked read-only before the local uncommitted upgrade. Re-run them after the owner publishes.

## Licensing and project ownership gate

Before publishing or republishing, verify:

- [ ] `LICENSE` is present and reflects the intended source-available non-commercial license.
- [ ] `NOTICE.md` is present.
- [ ] `docs/LICENSING_AND_COMMERCIAL_USE.md` is present.
- [ ] README clearly identifies the official repository and maintainer.
- [ ] README states that commercial use, hosted clones, redistribution, rebranding, and competing derivative products require written permission.
- [ ] README links to `LICENSE`, `NOTICE.md`, and `docs/LICENSING_AND_COMMERCIAL_USE.md`.
- [ ] `docs/README.md` links to `LICENSING_AND_COMMERCIAL_USE.md`.
- [ ] No unintended permissive or copyleft license file remains.
- [ ] No private business roadmap, private prompts, assistant instruction files, local review files, or internal notes are tracked.
