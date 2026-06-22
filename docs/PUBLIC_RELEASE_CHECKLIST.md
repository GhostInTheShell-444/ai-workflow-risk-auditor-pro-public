# Public Release Checklist

This checklist is a human approval gate. The repository must remain private until every P0 item is complete and an authorized owner explicitly approves a visibility change.

## P0 — blockers

- [ ] Complete a final human privacy and visual review of every screenshot.
- [x] Verify the repository remains private during iteration.
- [ ] Obtain explicit final human approval before any visibility change.
- [x] Select and include a license (currently MIT; confirm this remains the intended legal choice).
- [ ] Render and review the README as an external visitor would see it.
- [ ] Test installation on Ubuntu/Debian Linux.
- [ ] Test installation on macOS.
- [ ] Test installation on Windows PowerShell.
- [ ] Confirm GitHub Actions is green for the final commit after the final push.
- [ ] Scan tracked and proposed files for real email addresses, local paths, machine names, and personal notes.
- [ ] Scan tracked and proposed files for credentials, secrets, tokens, cookies, and environment values.
- [ ] Confirm no private review reports or internal instruction files are tracked or linked.
- [ ] Confirm no runtime database, virtual environment, cache, bytecode, log, environment file, or Streamlit secrets file is tracked.
- [x] Set the GitHub About description to the approved one-sentence description; recheck before launch.
- [ ] Set and review repository topics.
- [ ] Add and privacy-review a 1280×640 social preview.
- [ ] Run final link, image-path, Markdown, test, and localhost smoke checks.
- [ ] Record final human GO decision to switch visibility; automation must not make this decision.

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

## Final launch record

- Approval owner:
- Approval date:
- Approved commit:
- Final CI run:
- Screenshot review completed by:
- License confirmed by:
- Visibility changed manually by:

Leave this record blank during private iteration.
