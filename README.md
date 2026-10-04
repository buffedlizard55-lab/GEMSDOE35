# GEMSDOE35 — DOE GEMS fault-discovery experiments

> **Project charter:** reread this entire section before any substantive project work. Then check [`AGENTS.md`](AGENTS.md), the [hypothesis register](docs/hypotheses.md), and the latest [experiment report](reports/latest.json). Never turn a local proxy result into a DrivenData score claim.

## Current deliverable — local-proxy-screened candidate GeoTIFF

**[⬇ Download the uniquely named candidate TIFF](docs/downloads/gemsdoe35-h35-01-e58e5dbee6-20261004T164802Z-candidate.tif)** · [Executive summary and upload steps](docs/executive-summary.html) · [Project site](docs/index.html)

Filename: `gemsdoe35-h35-01-e58e5dbee6-20261004T164802Z-candidate.tif`<br>
DrivenData submission name: `GEMSDOE35-H35-01-e58e5dbee6`<br>
Suggested note: `GEMSDOE35 H35-01 LHS h35-01-e58e5dbee6; NW blocked proxy DTI delta +0.0103 vs tmi_hg; owner mirror unverified; not organizer-scored.`

**Important:** this is a unique, format-validated **candidate**, not an organizer-scored submission and not a forecast of its leaderboard score. It passes this repository's spatial-blocked screen only against the single-scale supplied `tmi_hg` proxy incumbent (the checkout contained no prior model or holdout result), on local owner-mirrored public catalogue labels. Those labels are existing faults; the competition's initial private test set contains newly identified fault pixels. The input mirror matches its own hashes, but is not authenticated as organizer-provided. Review these caveats and the official rules before spending a weekly submission slot. No slot has been spent automatically.

### Evidence summary (kept in separate score categories)

- **Local proxy result:** selected H35-01 candidate DTI was **0.026904** versus **0.016573** for the matched-mass single-scale `tmi_hg` ranking in the frozen NW quadrant (**Δ +0.010331**). The three development-block deltas were all positive; their mean was **+0.014452**. This is a local, spatially blocked screen on the owner mirror—not a leaderboard-score estimate and not private-test evidence. Full fold values, exact config and input hashes are in [`reports/h35-01-20261004T164802Z-e58e5dbee6.json`](reports/h35-01-20261004T164802Z-e58e5dbee6.json).
- **Public leaderboard observation (2026-10-04 UTC):** official board leader `nchuzhoy` **0.3262**, second `kinghorton42` **0.3222**, and `DARD` **0.3195** in third. These are public-board values only: [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).
- **Reported H33 value:** the attribution of **0.2778** to H33 is unverified. The public page shows 0.2778 for `extradr19` (rank 13) on the dated snapshot, but no verified file/submission link connects that row to H33. The owner-maintained [GEMSDOE32 H33 PR #9](https://github.com/buffedlizard55-lab/GEMSDOE32/pull/9) labels H33-2-B2 as a projected live 0.2747 (a model, not a score) and says there is no organizer score for those artifacts. A public score above 0.2778 is plainly plausible because the page already lists higher scores; exceeding 0.3262 or winning either prize round is unknown.
- **Organizer-scored outcome:** none for this TIFF. Do not describe the local DTI as the public leaderboard, private initial-round, or final-round score.

### TIFF validation

The candidate was reopened and checked against the local template and labels: **single-band float32**, shape **3292 × 3730**, **EPSG:32611**, 100 m transform, exact local-template bounds, NaN outside the footprint, finite values in **[0, 1]** inside. It contains 51,205 positive cells over the 5,167,373-cell finite scoring footprint. SHA-256: `5d26cdea082e18e97b693365de0fcfb41f97a432e18ff138d08cd7c622679929`. Machine-readable checks: [`reports/submission_validation.json`](reports/submission_validation.json) and the candidate receipt in the experiment report. This confirms the local raster contract; it cannot authenticate the official data grid independently of the login-walled organizer download.

## Project charter — original task prompt preserved for future work

> Review and improve the GEMSDOE35 repository to pursue a top result in DrivenData DOE GEMS competition #306. Preserve the user’s full prompt and Arena Core Values (“Maximize P(Win)” and “Own the Outcome”) as a project charter in `README.md`, to be reread before substantive work. Provide an obvious executive summary/site entry point and an easy-to-download, uniquely named single-band GeoTIFF submission with a concise DrivenData note; ensure values are within `[0,1]` and match official submission grid/CRS/resolution/bounds.
>
> Research and explain the reported 0.2778 H33 score and whether a higher score is plausible, grounding claims in verified sources and separating public leaderboard observations, user-reported scores, local proxy results, and organizer-scored outcomes. The current official page’s leader is 0.3262, not 0.3195. Generate 3–5 previously untried geological hypotheses, each naming layers, physical signature, why it may reveal faults absent from USGS/INGENIOUS, differences from this repo’s implementation, expected DTI improvement, implementation cost, and any required free official external source and whether it is obtainable. Enumerate varying design dimensions and use Latin hypercube sampling rather than hunch-named candidate batches; retire a dimension only after its holdout DTI effect is well-estimated. Validate the top candidate on spatially blocked holdout before any weekly submission slot; do not spend a slot unless it beats the holdout incumbent.
>
> Work autonomously where possible, verify claims line by line with linked sources, flag irregularities and blockers, run three implementation/review passes, suggest remaining work/limitations, and create/merge a pull request if tool permissions permit. Do not bypass DrivenData authentication or invent performance evidence.

### Arena Core Values

- **Maximize P(Win):** prioritize useful, falsifiable geological hypotheses and measured holdout gains; use designed experiments rather than hunch-named batches; do not spend a scarce competition slot on an untested or holdout-losing candidate.
- **Own the Outcome:** preserve data provenance, source links, exact configurations, checksums, validation reports, failures and limitations. Never claim organizer authentication, public score, private score, novelty, or success without evidence.

### Standing project rules

1. This branch's goal is to compete strongly, not to promise a win. The public leaderboard and hidden/private evaluations are different outcomes.
2. Before substantive work, reread this charter and review the full repository. The hypothesis register must precede a detector, the LHS design must enumerate varied and fixed dimensions, and a factor may be retired only after its holdout DTI effect is adequately estimated.
3. Keep the official scoring distinction: new fault means a fault pixel not already captured by USGS/INGENIOUS, including newly mapped geometry in an existing system ([staff definition](https://community.drivendata.org/t/where-do-you-draw-the-line/11536/2)). DrivenData staff confirmed that known catalogue pixels are masked **pixel-exactly**; nearby predictions still receive ordinary penalties, and new pixels can lie within 300 m of known traces ([scoring clarification](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4)). Do not buffer-suppress candidate pixels around known faults.
4. Do not bypass DrivenData authentication or invent data/performance. Public-mirror hashes establish mirror consistency only. Preserve provenance caveats in reports and site copy.
5. A candidate must improve on the declared local holdout incumbent before any slot is considered. A local pass is not a private-score prediction. No slot is used automatically.
6. Run the three review passes: (1) implement and verify; (2) inspect and fix assumptions, bugs and edge cases; (3) recheck the full prompt and deliverables. Log material corrections, including invalidated results.
7. Keep the TIFF single-band float32, within `[0,1]` on valid cells, NaN/nodata outside, on the exact official grid when authenticated official data is available. Use a unique filename and concise identifying note.
8. Suggest remaining work honestly, and create/merge a pull request if permissions allow. Keep all work on the Arena-tracked branch `arena/01a107a8-gemsdoe35`.

## Data provenance and blockers

The official DrivenData data page requires an enrolled login and could not be accessed here. The locally used features, labels and template were reassembled from the public `buffedlizard55-lab/GEMSDOE` bridge, which pins these SHA-256 values:

- `training_features.tif`: `4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5`
- `labels.tif`: `7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093`
- `sample_submission.tif`: `2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc`

A sanitized pin of the upstream bridge manifest SHA and file/part hashes is preserved at [`docs/evidence/owner-mirror-manifest.json`](docs/evidence/owner-mirror-manifest.json); third-party share URLs are intentionally omitted. The hash-verified reassembly receipt is [`reports/owner-mirror-reassembly.json`](reports/owner-mirror-reassembly.json). This is not organizer authentication or a licence determination. Two data-quality irregularities are recorded: (1) the mirrored sample's finite values equal the known labels, despite the official page describing a total-fault-absence sample—the code reads its grid/footprint only and never uses its values as a prediction or baseline; (2) each of the six selected feature bands has 3,061 float32 sentinel cells inside the finite label/template footprint. The loader masks these cells and the derivative code nearest-fills from valid neighbours; their sensitivity has not been separately measured. The [official competition page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) says its input layers are EPSG:32611 at 100 m and specifies the GeoTIFF output contract; additional manual-review sources are in the [hypothesis/source register](docs/hypotheses.md#sources-for-manual-review).

The reassembly command can reproduce the mirror files from that public bridge if the ignored `data/raw/` files disappear:

```bash
python scripts/reassemble_owner_mirror.py  # public owner mirror; NOT official authentication
python scripts/prepare_data.py
```

For verified organizer data, use the enrolled account and official [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), then place the authorized files at `data/raw/training_features.tif`, `data/raw/labels.tif`, and `data/raw/sample_submission.tif`. `prepare_data.py` checks grid, mask, value and hash metadata; it does not log in or fetch private files.

## Reproduce the experiment

Requirements: Python ≥3.10, NumPy, SciPy, Rasterio, pytest; CPU sufficient, no GPU model training in this H35-01 detector.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
python scripts/prepare_data.py
python -m pytest -q
python scripts/run_experiment.py
```

The eight-row mixed-factor LHS and all continuous/categorical/fixed dimensions are in [`configs/h35-01-lhs.json`](configs/h35-01-lhs.json). The run compares three contiguous development quadrants, selects a configuration, and evaluates the frozen NW spatial block once. On this machine the full eight-candidate CPU experiment took about ten minutes. A candidate TIFF is emitted only when all development and frozen-holdout DTI deltas beat the single-scale `tmi_hg` baseline. `--require-pass` makes a failed screen return exit code 2; a no-pass run writes a report and no TIFF.

## What remains before any competition upload

1. **Authenticate inputs against the enrolled DrivenData download.** The public mirror is not official evidence; if official files differ, prepare them locally and rerun the pipeline. Do not send credentials to this repository or attempt an unauthenticated bypass.
2. **Treat H35-01 as a screening candidate only.** The existing-label spatial holdout is not the hidden-new-fault population. No public/private leaderboard score has been received for this TIFF.
3. **Continue with separately designed tests for H35-02 and H35-03.** H35-04 first needs a local coverage/CRS/resolution/license audit of the publicly listed USGS conductance maps. Retire a factor only after replicated, blocked effects and uncertainty/interactions are sufficiently estimated.
4. **Submit manually only if the enrolled competitor accepts the provenance caveat, checks current official rules/eligibility, and chooses to spend one of the limited weekly slots.** The script never accesses DrivenData or submits automatically.

## Research and project site

- [Project homepage / download entry](docs/index.html)
- [Executive summary / submission instructions](docs/executive-summary.html)
- [Ranked geological hypotheses and source register](docs/hypotheses.md)
- [Claim-by-claim source register and irregularity ledger](docs/source-register.md)
- [Designed experiment protocol and parameter retirement rule](docs/design-of-experiments.md)
- [Latest run pointer](reports/latest.json)
- [Submission validation receipt](reports/submission_validation.json)

## Review passes completed for this delivery

1. **Implement and verify:** package, exact DTI implementation, deterministic mixed LHS, raster I/O, H35-01 transform, spatial holdout, candidate export, and tests.
2. **Review and fix:** discovered the organizer's pixel-exact known-fault-mask ruling; invalidated the first buffered run and removed every catalogue-neighbourhood buffer from the design/output; regenerated the LHS and full holdout; removed the NumPy array from JSON diagnostics; tested owner-mirror reassembly.
3. **Full request and edge-case recheck:** removed a no-op label-collar path after proving it was disjoint from the scored cores; rechecked the selected candidate and reproduced every block DTI within 1e-12; reran the test suite; reopened the TIFF against the local mirror grid; checked CRS/resolution/transform/mask/range/hash and source links; verified site/download paths; and reviewed charter/limitations.
