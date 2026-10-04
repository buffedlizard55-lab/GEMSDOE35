# GEMSDOE35 — DOE GEMS fault-discovery experiments

> **Project charter:** reread this entire section before any substantive project work. Then check [`AGENTS.md`](AGENTS.md), the [hypothesis register](docs/hypotheses.md), and the latest [experiment report](reports/latest.json). Never turn a local proxy result into a DrivenData score claim.

## Mandatory continuity reading

This README is the concise project charter. [`docs/original-project-prompt.md`](docs/original-project-prompt.md) is a normalized, consolidated task register of the user-supplied brief—not a verbatim transcript—and preserves its acceptance criteria, historical score claims, source links, site/submission requirements, Core Values, and verification constraints. At the start of every substantive session, read this charter, the task register, [`AGENTS.md`](AGENTS.md), the current hypothesis register, the experiment protocol, and the current evidence report. If the brief conflicts with official rules or staff clarifications, follow the official source and record the conflict; do not invent a workaround.

## Current artifact — unique H35-04 experiment; promotion gate FAILED

**[⬇ Download the newly generated, locally unique H35-04 TIFF](docs/downloads/gemsdoe35-h35-04-2101f9ab04-20261004T211253030616Z-candidate.tif)** · [Executive summary and download notes](docs/executive-summary.html) · [Project site](docs/index.html)

Filename: `gemsdoe35-h35-04-2101f9ab04-20261004T211253030616Z-candidate.tif`<br>
Local DrivenData name: `GEMSDOE35-H35-04-2101f9ab04-20261004T211253030616Z`<br>
Identifying note: `GEMSDOE35 H35-04 cross-physics LHS h35-04-2101f9ab04; proxy gate FAILED; unverified owner mirror; not organizer-scored.`

**Do not submit this file on the present evidence.** It is a newly generated H35-04 cross-physics edge-concurrence experiment, not copied from any previous file. Its prediction array is unique against matching-shape/matching-footprint GeoTIFFs in this repository's downloads folder only; no global archive of previous competition rasters was supplied. The preregistered spatial proxy gate **failed** versus the H35-01 incumbent (mean ΔDTI −0.000129; 4/6 outer tiles positive; minimum was 5/6 and positive mean). The file is provided as an experimental/research artifact because the project requires an easy-to-download unique TIF; it is explicitly **not slot-eligible** and no weekly slot was used. This is not an organizer score, public/private leaderboard estimate, or evidence about the hidden newly identified fault set. The owner mirror matches its own pinned hashes but is not authenticated as organizer-provided.

### Evidence summary (kept in separate score categories)

- **Local proxy result:** selected H35-01 candidate DTI was **0.026904** versus **0.016573** for the matched-mass single-scale `tmi_hg` ranking in the frozen NW quadrant (**Δ +0.010331**). The three development-block deltas were all positive; their mean was **+0.014452**. This is a local, spatially blocked screen on the owner mirror—not a leaderboard-score estimate and not private-test evidence. Full fold values, exact config and input hashes are in [`reports/h35-01-20261004T164802Z-e58e5dbee6.json`](reports/h35-01-20261004T164802Z-e58e5dbee6.json).
- **Public leaderboard observation (2026-10-04 UTC):** official board leader `nchuzhoy` **0.3262**, second `kinghorton42` **0.3222**, and `DARD` **0.3195** in third. These are public-board values only: [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).
- **Reported H33 value:** the attribution of **0.2778** to H33 is unverified. The public page shows 0.2778 for `extradr19` (rank 13) on the dated snapshot, but no verified file/submission link connects that row to H33. The owner-maintained [GEMSDOE32 H33 PR #9](https://github.com/buffedlizard55-lab/GEMSDOE32/pull/9) reports a removal/pruning line and labels H33-2-B2 as a projected live 0.2747 (a model, not a score); it explicitly says no organizer score exists for those artifacts. Mechanistically, removing low-credit pixels could raise a Tversky-style score if avoided false-positive cost exceeds lost true-positive credit, but the public 0.2778 row cannot be explained or assigned to that artifact from the evidence available. This repository does not copy that buffer-pruning rule: staff say catalogue masking is pixel-exact and nearby predictions are scored normally. A public score above 0.2778 is plainly plausible because the page already lists higher scores; exceeding 0.3262 or winning either prize round is unknown.
- **Organizer-scored outcome:** none for this TIFF. Do not describe the local DTI as the public leaderboard, private initial-round, or final-round score.
- **H35-02 challenger (2026-10-04):** the mixed-LHS strain-discontinuity hypothesis failed its registered promotion gate. It was positive on only 2/3 development blocks and scored 0.016990 DTI on reused NW, below matched-mass `tmi_hg` (0.019426) and H35-01 rescored at exactly the challenger budget, 0.030867. All arms emitted 27,979 pixels at 1.1976%. No H35-02 TIFF was emitted. NW was a reused paired block, not independent confirmation. See the [corrected matched-budget report](reports/h35-02-20261004T180550Z-6882a35675.json); the earlier run is superseded because it compared unequal masses.
- **H35-03 historical challenger (2026-10-04):** the preregistered eight-row magnetic-low/flank-curvature LHS was evaluated using nested leave-one-tile-out selection over six 3×2 spatial blocks. Mean outer-fold ΔDTI was **+0.005324 vs `tmi_hg`** (4/6 positive), but **−0.002998 vs H35-01** (3/6 positive); all three arms matched actual emitted mass in every fold. It failed the predeclared 5/6-positive-and-positive-mean gate against both comparators. **No H35-03 TIFF was generated and no slot was used.** This is exploratory catalogue-label CV because the same geography was previously summarized by quadrants, and it says nothing quantitative about newly identified private faults. See the [full H35-03 report](reports/h35-03-20261004T185851097813Z-9388e69e81.json). H35-04 is the latest experimental download, but it also failed to beat the incumbent and is not slot-eligible.
- **Latest challenger H35-04 (2026-10-04):** preregistered eight-row mixed LHS over maximum scale, axial orientation power, multiphysics balance, emission fraction and a balanced `mag_anom`/RTP choice. The detector combines co-located magnetic, gravity and shear-strain edge strengths with axial-normal agreement. On six nested 3×2 spatial tiles, matched actual emissions gave mean ΔDTI **+0.007316 vs `tmi_hg`** (5/6 positive), but **−0.000129 vs H35-01** (4/6 positive). The positive mean and 5/6 incumbent promotion conditions both failed. To fulfill the download deliverable without using a competition slot, an experimental unique TIF was emitted, locally deduplicated and explicitly marked **not slot-eligible**. It contains 45,869 positive cells. The holdout geography has been exposed in earlier summaries and labels are known catalogue faults, so evidence is exploratory only. Full report: [`reports/h35-04-20261004T211253030616Z-2101f9ab04.json`](reports/h35-04-20261004T211253030616Z-2101f9ab04.json).

### H35-04 TIFF validation

The new candidate was reopened and checked against the local owner-mirror template: **single-band float32**, shape **3730 × 3292**, **EPSG:32611**, 100 m transform and exact local-template bounds; NaN outside the finite footprint; all 5,167,373 in-footprint values finite and within **[0, 1]**. It contains **45,869** positive cells. GeoTIFF SHA-256: `056e8a3cb954ae3e6dee2c993e569ef0c60d42c24f29b44487fef91a0993bfa3`. Canonical prediction-array SHA-256: `4f6885d3c71414a1ffe677cd68bdf3615fbfffd0081fafd3e880d2d55b164875`; exact scan found no matching same-grid/footprint file in local downloads. Machine checks: [`reports/h35-04-submission-validation.json`](reports/h35-04-submission-validation.json) and nested/provenance/duplicate checks in [`reports/h35-04-20261004T211253030616Z-2101f9ab04.json`](reports/h35-04-20261004T211253030616Z-2101f9ab04.json). These verify local raster format and local-folder difference; they cannot authenticate the official data grid or prove uniqueness against files not supplied.

## Project charter — normalized original request preserved for future work

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
8. The September 2026 GEMS Prize Official Rules were reviewed in full. They allow up to three feedback submissions per week as specified by the platform, but require one final selected submission for both prize rounds; finalists must provide reproducible code/assets and documentation. Generative AI is allowed but its extent and use across submission elements must be disclosed in the final narrative. The suggested disclosure is in [`docs/executive-summary.html`](docs/executive-summary.html); the competitor must verify and own it.
9. Suggest remaining work honestly, and create/merge a pull request if permissions allow. Keep all work on the Arena-tracked branch `arena/01a10896-gemsdoe35`.

## Data provenance and blockers

The official DrivenData data page requires an enrolled login and could not be accessed here. The locally used features, labels and template were reassembled from the public `buffedlizard55-lab/GEMSDOE` bridge, which pins these SHA-256 values:

- `training_features.tif`: `4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5`
- `labels.tif`: `7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093`
- `sample_submission.tif`: `2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc`

A sanitized pin of the upstream bridge manifest SHA and file/part hashes is preserved at [`docs/evidence/owner-mirror-manifest.json`](docs/evidence/owner-mirror-manifest.json); third-party share URLs are intentionally omitted. The hash-verified reassembly receipt is [`reports/owner-mirror-reassembly.json`](reports/owner-mirror-reassembly.json). This is not organizer authentication or a licence determination. Two data-quality irregularities are recorded: (1) the mirrored sample's finite values equal the known labels, despite the official page describing a total-fault-absence sample—the code reads its grid/footprint only and never uses its values as a prediction or baseline; (2) each of the six selected feature bands has 3,061 float32 sentinel cells inside the finite label/template footprint. The loader masks these cells and the derivative code nearest-fills from valid neighbours; their sensitivity has not been separately measured. The [official competition page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) says its input layers are EPSG:32611 at 100 m and specifies the GeoTIFF output contract; additional manual-review sources are in the [hypothesis/source register](docs/hypotheses.md#sources-for-manual-review).

The user-referenced `scripts/download_competition_data.sh` is not present in this checkout. No authenticated organizer-data downloader is implemented; the available reproducibility fallback can reassemble only the public owner-maintained mirror, not verify organizer provenance. It can reproduce the mirror files if the ignored `data/raw/` files disappear:

```bash
python scripts/reassemble_owner_mirror.py  # public owner mirror; NOT official authentication
python scripts/prepare_data.py
```

For verified organizer data, use the enrolled account and official [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), then place the authorized files at `data/raw/training_features.tif`, `data/raw/labels.tif`, and `data/raw/sample_submission.tif`. `prepare_data.py` checks grid, mask, value and hash metadata; it does not log in or fetch private files.

## Reproduce the experiment

Requirements: Python ≥3.10, NumPy, SciPy, Rasterio, pytest; CPU sufficient for the deterministic H35-01 to H35-04 raster detectors; the reference U-Net is a separate GPU-accelerated approach.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
python scripts/prepare_data.py
python -m pytest -q
python scripts/run_experiment.py  # H35-01 reproduction
python scripts/run_h35_03.py --require-pass  # historical preregistered challenger; gate failed
python scripts/run_h35_04.py --export-experimental  # rerun the registered H35-04 screen; failed gates never spend a slot
```

The eight-row mixed-factor LHS and all continuous/categorical/fixed dimensions are in [`configs/h35-01-lhs.json`](configs/h35-01-lhs.json). The run compares three contiguous development quadrants, selects a configuration, and evaluates the frozen NW spatial block once. A candidate TIFF is emitted only when all development and frozen-holdout DTI deltas beat the single-scale `tmi_hg` baseline. `--require-pass` makes a failed screen return exit code 2; a no-pass run writes a report and no TIFF.


H35-04 is preregistered in [`configs/h35-04-lhs.json`](configs/h35-04-lhs.json) and implemented in `features.py`/`scripts/run_h35_04.py`. Four numeric factors are Latin-stratified across eight rows, with `mag_anom`/RTP balanced 4/4; the selected transform tests co-located magnetic/gravity/shear-strain edges and edge-normal agreement. Nested selection compares each tile with the other five, then matches actual emitted mass against `tmi_hg` and H35-01. Its gate failed (mean Δ −0.000129 vs H35-01, 4/6 positive), so the script only writes a TIF when the gate passes or `--export-experimental` is deliberately requested. That explicit flag created the file linked above for local research; it marks the output not slot-eligible. The script never uploads or logs into DrivenData.

H35-03 is a separately preregistered eight-row mixed LHS in [`configs/h35-03-lhs.json`](configs/h35-03-lhs.json), stratifying five continuous dimensions and balancing `mag_anom`/RTP/TMI 3/3/2. It uses six 3×2 spatial cores with 30-pixel margins because equal-index footprint audit showed that 3×3 had empty/undersupported tiles and 4×2's minimum support was only 654 positive pixels. It selects one LHS setting independently for each outer tile from the other five and compares all arms at the exact same actual emitted mass. The 2026-10-04 run failed against the frozen H35-01 incumbent; no TIF was created. The run script exits 2 with `--require-pass` on failure and never accesses or submits to DrivenData.

## What remains before any competition upload

1. **Authenticate inputs against the enrolled DrivenData download.** The public mirror is not official evidence; if official files differ, prepare them locally and rerun the pipeline. Do not send credentials to this repository or attempt an unauthenticated bypass.
2. **Treat H35-04 as an experimental artifact, not a slot candidate.** Its registered proxy screen failed versus H35-01 at matched actual mass (−0.000129 mean delta; 4/6 positive). A distinct file was produced only to satisfy the local easy-download/reproducibility requirement; it is marked not slot-eligible. The existing-label spatial holdout is not the hidden-new-fault population. No public/private leaderboard score has been received for either local TIFF.
3. **Keep a dated public-board snapshot; do not scrape DrivenData.** The official Terms of Use prohibit robot/spider/automatic site monitoring and manual monitoring/copying without prior written consent. The current board values are a point-in-time observation. A continuous feed requires prior written permission or an organizer-approved API; this repository does not automate leaderboard access.
4. **Do not retune H35-03/H35-04 on exposed tiles.** H35-04's factor effects are not retired by one eight-row LHS. Next prioritize H35-05 seismicity gradients or H35-06 relief signatures using existing layers; H35-07 radiometric raw files are catalogued by USGS but the Area 2 GeoTIFF archive has not been transferred/aligned in this workspace. ScienceBase metadata exposes the official `22103_area2_tiffs.zip` download URI, size 241,738,690 bytes, and MD5 `2b927f17b8261380b72c2be9e1d46490`; the binary's actual transfer, raster CRS/coverage, and overlap with the competition template remain unchecked. Do not implement until downloaded, validated and license/rules suitability reviewed. Any new split of the same public labels remains exploratory; only genuinely new outer geography/labels can provide an untouched confirmation.
5. **Do not spend a competition slot on the present evidence.** No new candidate beat the frozen H35-01 holdout incumbent; only consider a future manual submission after a fresh, preregistered spatial screen beats it, official inputs/rights and current rules are verified, and the enrolled competitor independently decides to use a slot. The scripts never access DrivenData or submit automatically.

## Research and project site

- [Project homepage / download entry](docs/index.html)
- [Executive summary / submission instructions](docs/executive-summary.html)
- [Ranked geological hypotheses and source register](docs/hypotheses.md)
- [Claim-by-claim source register and irregularity ledger](docs/source-register.md)
- [Designed experiment protocol, H35-02/H35-03/H35-04 results, and parameter retirement rule](docs/design-of-experiments.md)
- [H35-04 latest screen](reports/h35-04-latest.json) · [H35-04 report and design](reports/h35-04-20261004T211253030616Z-2101f9ab04.json) · [H35-04 format receipt](reports/h35-04-submission-validation.json)
- [H35-03 nested spatial-LHS report](reports/h35-03-20261004T185851097813Z-9388e69e81.json) · [H35-03 latest pointer](reports/h35-03-latest.json)
- [H35-02 challenger report with matched incumbent budget](reports/h35-02-20261004T180550Z-6882a35675.json) · [superseded initial unequal-budget report](reports/h35-02-20261004T175239Z-6882a35675.json)
- [Full original project prompt archive](docs/original-project-prompt.md)
- [Current experimental TIF pointer (H35-04; not slot-eligible)](reports/latest.json) · [H35-03 screen](reports/h35-03-latest.json) · [H35-02 screen](reports/h35-02-latest.json)
- [Submission validation receipt](reports/submission_validation.json)
- [Exact prediction reconstruction receipt](reports/candidate-reconstruction.json)

## Review passes completed for the current delivery

1. **Implement and verify:** reviewed the full prompt/charter, official task/scoring/submission page, 2026-10-04 official leaderboard snapshot, reference solution, organizer staff clarifications on pixel-exact catalogue masking and new-fault scope, and source-register evidence. Preregistered four next hypotheses and the H35-04 mixed LHS before adding the detector. Reassembled the public owner-mirror inputs with hash checks, ran the six-tile nested spatial screen, emitted a local experimental TIF only with an explicit non-promotion flag, performed a local duplicate scan, and reopened the TIF for format/range checks.
2. **Review for bugs/assumptions:** fixed the script's missing H35-01 comparator bands; ensured all in-footprint cells remain finite (known-catalogue pixels are zero, NaN is only outside the sample footprint); checked exact actual emissions for all three comparator arms; marked slot eligibility false even independently of the failed proxy gate; identified historic spatial-fold exposure, owner-mirror provenance and target-population mismatch. Added synthetic detector tests and exact-format validation.
3. **Recheck against the full brief:** H35-04 averaged +0.007316 vs `tmi_hg` but −0.000129 vs H35-01 and was positive against H35-01 on 4/6 (gate requires positive mean and 5/6). The TIFF is a unique local research artifact, not a recommended submission. Confirmed SHA, shape, EPSG:32611, 100 m transform, finite [0,1] in-footprint values, NaN outside and local duplicate absence; updated README, site, hypothesis/source registers, receipts and run instructions. Full suite: **29 passed**. No organizer/public/private score was inferred; no DrivenData slot was consumed.
