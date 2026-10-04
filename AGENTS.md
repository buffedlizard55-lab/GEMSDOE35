# Continuity instructions

Before substantive work, read the full project charter and standing rules in [`README.md`](README.md), the complete durable task register in [`docs/original-project-prompt.md`](docs/original-project-prompt.md), then review [`docs/hypotheses.md`](docs/hypotheses.md), [`docs/design-of-experiments.md`](docs/design-of-experiments.md), [`reports/latest.json`](reports/latest.json), and [`reports/h35-02-latest.json`](reports/h35-02-latest.json).

- Always stay on the Arena-tracked branch `arena/01a10801-gemsdoe35`; do not switch branches.
- The current downloadable candidate is H35-01 at `docs/downloads/gemsdoe35-h35-01-e58e5dbee6-20261004T164802Z-candidate.tif`. It is local-proxy-screened and format-validated against the owner mirror, but not organizer-authenticated or scored.
- H35-02's 2026-10-04 mixed-LHS screen failed the predeclared promotion gate; no H35-02 TIFF was emitted. Use corrected report `reports/h35-02-20261004T180550Z-6882a35675.json`: H35-01 was rescored at the challenger fraction and all candidate/baseline arms emitted 27,979 NW pixels (H35-01 DTI 0.030867 vs H35-02 DTI 0.016990). The earlier `175239Z` report is retained but superseded because its incumbent comparison used unequal budgets.
- H35-01's NW score has been examined. H35-02 reused NW as a paired challenger block, so it is not an independent confirmation. Do not continue tuning against NW; future confirmation requires preregistered fresh outer geography or a nested multi-block design.
- The spatial margin erodes split boundaries; it is not a catalogue or training-label buffer. Follow DrivenData staff's exact-pixel known-fault mask ruling; never suppress the surrounding 300 m or other buffer.
- Treat owner-mirror rasters as unverified by DrivenData. Do not fetch or use login-walled organizer data without an enrolled authorized account; never automate login or request/store credentials.
- Do not automatically scrape DrivenData's leaderboard: the current Terms of Use prohibit automated monitoring/copying and unauthorized manual monitoring/copying. Use date-stamped reviewed snapshots unless written permission or an approved API is available.
- Preserve prior artifacts, reports, failed runs, source links, configuration provenance and checksums. Do not regenerate an identical prediction under a new name or overwrite history.
- Update code, tests, reports, README and site evidence when a new validated result supersedes the current candidate. No script may submit a competition entry automatically.
