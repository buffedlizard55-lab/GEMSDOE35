# Continuity instructions

Before any substantive change, reread the Project Charter and Standing Project Rules at the top of [`README.md`](README.md), then review [`docs/hypotheses.md`](docs/hypotheses.md), [`docs/design-of-experiments.md`](docs/design-of-experiments.md), and [`reports/latest.json`](reports/latest.json).

- Keep work on `arena/01a107a8-gemsdoe35`.
- Do not use the invalidated buffered experiment as evidence; only the exact-pixel-mask H35-01 report is current. The spatial margin erodes block boundaries; it is not a catalogue or training-label buffer.
- Treat the candidate TIFF as a local-proxy-screened artifact, not an organizer or leaderboard score.
- Preserve the official staff ruling: exact known-catalogue pixel mask only; do not suppress the surrounding 300 m or other buffer.
- Do not fetch or use login-walled DrivenData data without the enrolled account. The GitHub mirror is not organizer-authenticated.
- Update `reports/latest.json`, docs, and tests when a new experiment supersedes the current candidate; never overwrite a prior artifact in a way that hides its history.
