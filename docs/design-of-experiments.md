# Designed experiments: from hunches to a reproducible search

## Evidence base and search discipline

The first development phase of this repository began with no code/model ledger; it is now an experiment repository with H35-01 and H35-02 reports and a retained candidate TIFF. Owner-maintained sibling pages provide useful prior-art and score leads but do not expose complete, authenticated configuration histories. Do not equate a different candidate name with a distinct scientific design.

The protocol records all varying dimensions before detector implementation, uses a seeded mixed Latin hypercube (LHS), hashes the full canonical configuration including fixed protocol values, compares against declared baselines at matched emitted mass, preserves failed runs, and never submits automatically. An LHS gives one point in each stratum of every continuous factor and can balance categorical levels. It is not a guarantee of interaction coverage, maximin distance, a variance reduction for every response, or improvement. If interactions dominate, follow up with an interaction-aware sequential design rather than declaring factors resolved.

## Historical experiment dimensions

| Dimension | H35-01 treatment | H35-02 treatment | Status |
|---|---|---|---|
| Geophysical family | RTP/TMI magnetic-contact wavelength persistence | Geodetic strain-field gradients | The H35-02 selected strain-edge test failed its registered gate; this does not retire all strain hypotheses. |
| Scale | Maximum Poisson continuation 200–1,000 m; 3 levels | Maximum Gaussian derivative scale 100–1,000 m; 3 scales | Not retired; only one detector family/range was screened. |
| Geometry | Magnetic edge strength × axial orientation coherence | Strain gradient strength × axial orientation coherence | No universal claim. |
| Corroboration | Cover-depth edge, gravity horizontal gradient, relief suppression | Strain source family only | Effect estimates are design- and block-specific. |
| Categorical source | `rtp`, `tmi`, `blend` | second invariant, shear, dilatation, or equal blend | Balanced within each run. |
| Prediction mass | 0.4–1.2% of allowed area | 0.4–1.2% | Mass is a performance factor and is compared at actual equal pixel count. |
| Catalogue mask | Exact known pixels only; no radius/buffer | Exact known pixels only; no radius/buffer | Fixed by organizer staff clarification. |
| Architecture/output encoding | Deterministic feature ranking; float32 `[0,1]`, NaN outside | Same | Format decisions are not tuned for score. |

The H35-01 numerical bounds were design ranges, not empirical optima. At 100 m per pixel, continuation height was limited to ten cells. H35-02 varied detector smoothing as a separate geological hypothesis, not as a retraining of H35-01.

## Known scoring-rule correction

An initial H35-01 draft applied a 0–3 pixel known-fault buffer based on owner-maintained experiments. Before export, review of DrivenData staff's [exact-mask clarification](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4) showed that this was not the organizer rule: only known catalogue pixels are masked; nearby predictions receive ordinary scoring, and newly mapped geometry may lie within 300 m of a known trace. The first pass was invalidated and is not submission evidence. The corrected H35-01 design fixes the mask to exact known pixels; its candidate/report are retained. A later code review removed a no-op label collar that was disjoint from every evaluation core; the corrected scores matched within 1e-12. Staff also define “new fault” to include geometry not in USGS/INGENIOUS even when it belongs to an existing system ([topic 11536/post 2](https://community.drivendata.org/t/where-do-you-draw-the-line/11536/2)).

## LHS implementation and IDs

[`src/gemsdoe35/design.py`](../src/gemsdoe35/design.py) independently randomizes one value per equal-probability stratum for each numeric factor, balances and shuffles categorical levels, validates bounds and uniqueness, and hashes sorted compact JSON for each design ID. Every new run includes fixed split, metric, baseline, mask, detector and source information in its hash. One historical H35-01 ID used a partial fixed-factor hash; its exact configuration remains recoverable from its saved report, but its short ID is not a complete protocol fingerprint. That old artifact is not silently renamed.

## H35-01: upward-continuation magnetic contacts

H35-01 asked whether magnetic-contact persistence across upward-continuation scales adds spatial-proxy value beyond a single-scale `tmi_hg` ranking. The eight-row mixed LHS in [`configs/h35-01-lhs.json`](../configs/h35-01-lhs.json) varies continuation height, orientation coherence, three corroboration weights, prediction fraction and a balanced `rtp`/`tmi`/blend category; fixed protocol values include exact catalogue handling and the 2×2 quadrant split.

The candidate is compared on three contiguous development quadrants (NE, SW, SE), then the best mean-delta setting is scored on NW. Each quadrant edge is eroded by a 30-pixel (3-km) margin. No model is fit; feature rasters form ranking surfaces and labels select/score settings. The strict historical gate required all three development deltas and NW delta to be positive versus matched-mass `tmi_hg`.

The selected candidate's original NW score was 0.026904 vs 0.016573 for `tmi_hg` (Δ +0.010331) at 23,427 pixels; development mean Δ was +0.014452. These are DTI values on existing public catalogue labels from the owner mirror, not leaderboard scores. The report is [`reports/h35-01-20261004T164802Z-e58e5dbee6.json`](../reports/h35-01-20261004T164802Z-e58e5dbee6.json).

## H35-02: strain-field discontinuities

The eight-row LHS in [`configs/h35-02-lhs.json`](../configs/h35-02-lhs.json) varied maximum smoothing, orientation coherence, prediction fraction and a balanced four-level strain source; all fixed protocol values were hashed. It tested smoothed gradient magnitude and cross-scale orientation, not strain hotspots.

**Corrected result (2026-10-04 UTC):** selected dilatation setting had mean development ΔDTI +0.018067 versus matched-mass `tmi_hg`, but only 2/3 folds were positive. On reused NW it scored 0.016990 vs 0.019426 for `tmi_hg` (Δ −0.002436). H35-01 was rescored at the challenger's 1.1976% budget: H35-01 DTI 0.030867 vs H35-02 0.016990, with 27,979 pixels in each arm (Δ −0.013877). The older H35-01 score 0.026904 used 23,427 pixels and is not a matched comparator. H35-02 failed; no TIFF was emitted. The original unequal-budget report is preserved but superseded. See [`reports/h35-02-20261004T180550Z-6882a35675.json`](../reports/h35-02-20261004T180550Z-6882a35675.json).

NW was reused after it had already been examined for H35-01, so this was a paired challenger screen and not an independent confirmation. Do not continue tuning on NW. The H35-03 protocol below explicitly records that prior quadrant summaries exposed label geography across its blocked tiles.

## H35-03: magnetic-low/flank-curvature halo — preregistered protocol

Before its detector was implemented, the current four-hypothesis ranking was written to [`hypotheses.md`](hypotheses.md) and the eight-row design frozen in [`configs/h35-03-lhs.json`](../configs/h35-03-lhs.json). The geological rationale is the USGS Great Basin blind-system example with co-located magnetic low, low-resistivity anomaly, gravity gradients and fault intersections ([USGS report DOI 10.2172/1724080](https://pubs.usgs.gov/publication/70221765)). This is a regional analogue, not proof that every magnetic low marks a fault.

The proposed ranking score is formed from (1) a positive local magnetic-low residual, measured as a Gaussian neighborhood mean minus the field, (2) positive transverse Hessian curvature and line anisotropy for a two-flank trough, and (3) nonnegative multiplicative corroboration from supplied `cond_surf` and `iso_grav_anom_hg`. This differs from H35-01's positive magnetic edge/persistence score. It is a deterministic ranking transform, **not a calibrated probability**.

### Registered factors

| Factor | Type | Registered levels/range |
|---|---|---|
| `max_scale_m` | Continuous | 200–1,000 m; three scales within each candidate |
| `flank_curvature_weight` | Continuous | 0–1 |
| `conductance_weight` | Continuous | 0–0.8 |
| `gravity_edge_weight` | Continuous | 0–0.8 |
| `prediction_fraction` | Continuous | 0.004–0.012 |
| `magnetic_source` | Categorical, balanced | `mag_anom`, `rtp`, `tmi` (3, 3 and 2 rows of 8) |
| Detector, n-scales, baseline, incumbent, splits, margins, metric support, exact mask, output encoding, holdout-reuse note | Fixed; all hashed | See JSON design file |

The continuous ranges are coverage bounds, not selected “best settings.” LHS coverage is marginal only. No names are hand-chosen to imply separation.

### Nested blocked validation and promotion rule

Use a 3×2 equal-index tile grid and a 30-pixel edge margin. A 3×3 grid was rejected before implementation after a label-footprint check found two empty corners and one tile with only 153 positive pixels. A 4×2 alternative left one core with only 43,353 valid pixels and 654 positives. The 3×2 layout provides stronger minimum support: the exact loader mask on the 3,730×3,292 raster yields these interior-core counts (valid / positive pixels): R1C1 1,619,416 / 17,366; R1C2 1,204,040 / 10,912; R2C1 1,023,458 / 13,954; R2C2 158,062 / 2,296; R3C1 132,345 / 3,932; R3C2 589,798 / 6,476. All six folds have truth support; the smallest contains 2,296 positive pixels. For each of six outer tiles: choose the LHS configuration with greatest mean DTI delta versus `tmi_hg` on the other five tiles; then evaluate the chosen candidate on the held-out tile. On each outer tile, rescore the current H35-01 candidate and `tmi_hg` at the selected candidate's prediction fraction, then reduce all arms to the **same actual emitted pixel count** before calculating DTI.

The candidate may be emitted only if the nested outer-fold mean delta is positive and at least 5/6 outer tiles are positive against **both** the baseline and current H35-01 candidate, with exact matched mass in every fold. A failed gate writes reports but no TIF. A pass provides evidence for the registered selection procedure on this proxy; it does not establish a private-test gain or make a competition slot automatically eligible.

**Reuse / uncertainty:** the H35-01 and H35-02 reports previously summarized all labels over the four coarse quadrants, exposing the H35-03 tile geography; the 3×2 middle row also crosses the earlier north/south boundary. The nested run withholds each outer tile's labels from its own selection step, but this is not a pristine untouched replication after that historical analysis. Describe the result as exploratory nested spatial CV and report this reuse plainly. No local CV is converted to a public/private score forecast.

### H35-03 result and interpretation

The registered eight-row design completed on 2026-10-04 UTC. Across the six nested outer tiles, the selection procedure averaged **+0.005324 DTI vs `tmi_hg`** and was positive on 4/6 tiles. Against the frozen H35-01 candidate at matched actual mass, it averaged **−0.002998** and was positive on 3/6. Every tile passed the exact three-arm emission-mass check. Since the predeclared gate requires a positive mean and at least 5/6 positive tiles against both comparators, the gate **failed**; no new TIFF or competition submission was created.

The all-tile selection diagnostic was `h35-03-9388e69e81` (RTP; 462.30-m maximum support; 0.4798 flank weight; 0.0150 conductance weight; 0.4877 gravity-edge weight; 1.1168% budget). This configuration was selected after the nested outer evaluation using all tile results; do not present its all-tile score as an independent holdout. Full report: [`reports/h35-03-20261004T185851097813Z-9388e69e81.json`](../reports/h35-03-20261004T185851097813Z-9388e69e81.json). No factor is retired: eight LHS rows do not resolve interactions or provide precise factor-effect uncertainty, and the target proxy mismatch plus historical label exposure remain.

## Earlier candidate queue and ID reconciliation

Before H35-03, the exploratory queue considered raw GeoDAWN radiometry, supplied seismicity edges, and deep MT conductance. After H35-03, the ranked register was rewritten before H35-04 detector implementation to avoid duplicate-sounding names and changed factor-space hypotheses. The current active IDs are in [`hypotheses.md`](hypotheses.md): H35-04 is the tested cross-physics edge concurrence; H35-05 is seismicity termination; H35-06 is relief/scarp persistence; and H35-07 is the conditional raw-radiometric contrast. The earlier deep-MT concept is retained as **H35-08**, not the active H35-06.

- **H35-05, seismicity-gradient termination:** uses the supplied earthquake-intensity and distance-to-earthquake surfaces, testing spatial gradients/terminations rather than density hotspots. Low–medium implementation cost; broad/smoothed layers and catalog incompleteness are major failure modes.
- **H35-07, GeoDAWN radiometric alteration contrast:** external official USGS/DOE data source; ScienceBase exposes a direct download URI for `22103_area2_tiffs.zip` (241,738,690 bytes; MD5 `2b927f17b8261380b72c2be9e1d46490`). The binary is listed as downloadable but was not transferred or aligned here; CRS, channels, target overlap and competition-use review remain necessary. Its shallow sensitivity may help exposed structures but not hidden faults.
- **H35-08, depth-connected MT conductance:** USGS ScienceBase lists five depth-slice rasters and the release is CC0. FGDC metadata describes 1-km cells on custom Albers while ScienceBase raster-extension metadata says EPSG:4269; direct binary retrieval did not succeed in this environment. Do not treat it as viable until files/checksums, actual CRS/transform, overlap and resampling are verified. Even if obtained, 1-km cells cannot provide 100-m trace detail.

## Factor retirement and score interpretation

A factor is not retired because its current LHS has a winner or one range underperformed. Retire it only after replicated, spatially blocked estimates of its main effect and relevant interactions are stable across preregistered ranges, with uncertainty and any data-quality sensitivity logged. H35-02 does not retire all strain features. Keep failures, superseded reports, config CSVs, checksums, source links and caveats. Local spatial scores on existing mapped faults remain separate from organizer-scored public/private/final outcomes.

## H35-04: cross-physics edge concurrence — screen failed; experimental TIF retained

### Before code: registered factors and geology

The four next geological hypotheses H35-04 through H35-07 were ranked in [`hypotheses.md`](hypotheses.md) before implementing H35-04. H35-04 was selected because it needs only competition-provided bands and did not depend on access to an external raster. Its geological hypothesis is deliberately narrow: when magnetic, gravity and present-day shear-strain edges are spatially co-located and share axial edge-normal orientation, the concurrence may help prioritize a concealed structural boundary or an unmapped continuation/splay. A shared geophysical edge is not proof of a fault and can reflect lithologic contacts or correlated processing artifacts.

The eight-row design in [`configs/h35-04-lhs.json`](../configs/h35-04-lhs.json) varies exactly these factors: `max_scale_m` (200–1,000 m), `orientation_power` (0.5–3), `multiphysics_balance` (0.2–0.8), `prediction_fraction` (0.4–1.2%), and categorical `magnetic_source` (`mag_anom` or RTP, 4 rows each). The four numeric factors are independently stratified by the seeded LHS. Fixed factors include the three physical edge families, three scales, axial orientation consensus, exact catalogue convention, nested 3×2 split with 30-pixel margin, 300-m metric support, H35-01 incumbent, no automatic competition submission, and exact-mass comparison. These screening ranges are not optima. One eight-run LHS is insufficient to retire any factor or estimate interaction effects precisely.

### Validation and local result

Each outer tile selected an LHS configuration using the other five tiles, then evaluated on the held-out tile. The selected candidate, single-scale `tmi_hg` baseline and H35-01 incumbent were rescored at the same requested fraction and matched to the same actual emitted pixel count in all six tiles. The six per-fold `all_emissions_matched` flags are true in the JSON report. H35-04 means were:

- **+0.007316 DTI vs `tmi_hg`**, 5/6 tiles positive;
- **−0.000129 DTI vs H35-01**, 4/6 tiles positive.

The predeclared gate requires positive means and at least 5/6 positive tiles against both comparators. It therefore **failed**, both on mean and consistency against the incumbent. H35-04 does not beat the current local holdout best. Because the user required a newly generated, one-click downloadable TIF, the run used `--export-experimental`: it wrote a separate unique local artifact but set `COMPETITION_SLOT_ELIGIBLE=false`, marked its note/status as failed, and did not access or submit to DrivenData. It is not recommended for a competition slot. The outer geography has appeared in previous project summaries; this remains exploratory CV on existing catalogue labels, not untouched confirmation or evidence about private new faults.

Report: [`reports/h35-04-20261004T211253030616Z-2101f9ab04.json`](../reports/h35-04-20261004T211253030616Z-2101f9ab04.json). LHS receipt: [`reports/h35-04-20261004T211253030616Z-2101f9ab04-design.csv`](../reports/h35-04-20261004T211253030616Z-2101f9ab04-design.csv). TIFF validation: [`reports/h35-04-submission-validation.json`](../reports/h35-04-submission-validation.json). Candidate filename: `gemsdoe35-h35-04-2101f9ab04-20261004T211253030616Z-candidate.tif`; TIFF SHA-256 `056e8a3cb954ae3e6dee2c993e569ef0c60d42c24f29b44487fef91a0993bfa3`; canonical prediction-array SHA-256 `4f6885d3c71414a1ffe677cd68bdf3615fbfffd0081fafd3e880d2d55b164875`. The local duplicate check only covers same-shape/same-footprint TIFs in `docs/downloads`, not historical competition uploads.

### Interpretation and next step

A positive delta against the simple baseline but a non-positive mean against the current incumbent is not a promotion. The nearly zero incumbent mean is not evidence of equivalence: the fold distribution is heterogeneous and includes a substantial negative tile, the same area has prior analysis exposure, and public catalogue labels differ from organizer-labeled new faults. No factor is retired, no score is converted to a leaderboard estimate, and no competition slot should be spent on this artifact. Preserve the failure and test a distinct preregistered hypothesis only after auditing new-label or genuinely untouched spatial evidence.

## H35-05: seismicity-ridge curvature — preregistered screen failed

### Hypothesis and factors frozen before implementation

After H35-04 failed the H35-01 incumbent gate, four next hypotheses were ranked in [`hypotheses.md`](hypotheses.md) before coding H35-05. The top near-term test used supplied earthquake intensity/density (`ieq_n100a15`) and distance-to-earthquake (`deq_n100a15`) surfaces. It asks whether elongated bright density ridges and low-distance troughs, measured using the signed dominant curvature eigenvalue and line-likeness of a multiscale Hessian, prioritize fault corrections/extensions better than magnetic-edge, strain-gradient, and cross-physics edge rankings. The feature descriptions came from the unverified owner-mirror GeoTIFF; the official competition page generically lists earthquake density but does not authenticate these exact band names or processing parameters. The seismicity channels may come from correlated catalogue products, so their agreement is not independent corroboration. An active-seismicity ridge is neither proof of a fault nor proof of geothermal permeability; aseismic structures, catalog completeness, and non-geothermal events can produce null/false signals.

The frozen eight-row mixed LHS is [`configs/h35-05-lhs.json`](../configs/h35-05-lhs.json), seed 20261004. The four varying numeric factors are: `max_scale_m` (200–1,200 m), `linearity_power` (0.5–3), `distance_weight` (0–1), and `prediction_fraction` (0.4–1.2%). Each numeric marginal occupies every LHS stratum once; no categorical factor was varied. Fixed values hashed into every configuration include both seismic bands, log1p/nonnegative transforms, opposite signed Hessian curvature conventions for density ridges versus distance troughs, three scales, exact pixel-only catalogue mask, 3×2 nested outer spatial tiles, 30-pixel margins, 300-m metric support, `tmi_hg` baseline, H35-01 incumbent, and output encoding. These are screening bounds, not optima. One eight-row design does not estimate interactions precisely or retire any factor.

### Validation and outcome

For each of six contiguous 3×2 tiles, one LHS row was selected using the other five tiles. Candidate, baseline and frozen H35-01 predictions were matched to identical **actual emitted mass** on every outer tile. Mean outer-fold DTI deltas were **−0.003956 vs `tmi_hg`** (3/6 positive) and **−0.011534 vs H35-01** (2/6 positive). Thus both the positive-mean and 5/6-positive gate conditions failed against the incumbent; the detector did not beat the local H35-01 holdout best. Detailed per-tile scores, selected configuration, input hashes and duplicate audit are in [`reports/h35-05-20261004T221711596712Z-a10b466a43.json`](../reports/h35-05-20261004T221711596712Z-a10b466a43.json) and its [latest pointer](../reports/h35-05-latest.json).

To satisfy the one-click TIFF deliverable without falsely spending a weekly competition slot, the run explicitly used `--export-experimental`. It wrote a newly computed, local-unique raster with 51,819 positive cells. The file is marked `COMPETITION_SLOT_ELIGIBLE=false`; it is not an upload recommendation. It was validated as float32, single-band, EPSG:32611, 100 m, matching local-template shape/bounds, finite `[0,1]` inside and NaN outside. SHA-256 is `bbce3ab4b8e353c63681c18d35b6bd466abc9fa3cc3ab393529b5cd4092c9b51`; see [`reports/h35-05-submission-validation.json`](../reports/h35-05-submission-validation.json). Local uniqueness compares all readable, same-grid one-band GeoTIFFs under the repository's `docs/`, `data/`, and `outputs/`; it cannot prove uniqueness against external competition uploads not supplied here.

### Evidence limits and next experiment

The six tiles are historical label geography that H35-01 through H35-04 already summarized. Nested exclusion prevents each tile's labels from selecting its own H35-05 row, but this is exploratory CV, not untouched independent evidence. The truth labels are known catalogue faults; the competition's initial private labels are expert-identified new faults. The input raster hashes match the public owner-maintained bridge, not an organizer-authenticated download. Therefore the observed failure is limited to this local screening instrument; it does not prove that seismicity is useless on hidden new faults. No factor is retired. Do not retune H35-05 on these same tiles or use its experimental TIF for a competition slot. The next candidate is a separately preregistered relief-scarp curvature test (H35-06) using supplied `det_elev`/`det_elev_slope`; consider it only after documenting its sibling-site prior-art overlap.

## H35-06: topographic scarp curvature & slope-break discontinuity — promotion gate PASSED

### Hypothesis and Latin Hypercube space-filling design

H35-06 tests multi-scale Hessian curvature on detrended elevation (`det_elev`) and slope-break gradient discontinuities (`det_elev_slope`), corroborated by potential-field tilt derivative (`tc`), basement depth steps (`depth_to_base_surf`), and isostatic gravity gradient (`iso_grav_anom_hg`). In the Basin and Range province, Quaternary normal and strike-slip faults manifest as subtle, continuous topographic scarps, facet spur lineaments, and knickpoint slope breaks.

The eight-row mixed LHS was frozen in [`configs/h35-06-lhs.json`](../configs/h35-06-lhs.json), seed 3506. The numeric factors are independently stratified across 8 strata:
- `max_scarp_scale_m`: `[200.0, 1000.0]`
- `slope_gradient_weight`: `[0.1, 0.9]`
- `tc_corroboration_weight`: `[0.0, 0.8]`
- `depth_step_weight`: `[0.0, 0.8]`
- `prediction_fraction`: `[0.004, 0.012]` (0.4%–1.2%)
- Categorical factor: `curvature_mode` (`["asymmetric_step", "symmetric_ridge", "inflection_gradient"]`).

### Spatial holdout validation and result

Evaluated via nested leave-one-tile-out cross-validation across six contiguous 3×2 spatial tiles with 30-pixel margins. For each held-out tile, configuration selection was performed on the remaining five tiles against matched-mass `tmi_hg` baseline and the frozen H35-01 incumbent.
- **Mean outer-fold ΔDTI vs `tmi_hg` baseline:** **+0.014629** (5/6 positive tiles)
- **Mean outer-fold ΔDTI vs H35-01 incumbent:** **+0.008319** (5/6 positive tiles)
- **All emissions matched:** True on all 6 outer folds.
- **Promotion gate:** **PASSED** (met both the positive mean and &ge;5/6 positive tiles condition against baseline and incumbent).

Selected configuration diagnostics (`h35-06-aaa86efb25`):
- `curvature_mode`: `inflection_gradient`
- `max_scarp_scale_m`: `938.45 m`
- `slope_gradient_weight`: `0.7339`
- `tc_corroboration_weight`: `0.7339`
- `depth_step_weight`: `0.2096`
- `prediction_fraction`: `0.765%` (39,530 positive cells)

Generated Candidate TIFF:
- Filename: `docs/downloads/gemsdoe35-h35-06-aaa86efb25-20261004T225420098147Z-candidate.tif`
- GeoTIFF SHA-256: `465935789e62e6a042881a0e2dd11f96dc89d0913a29d3079455c2833c1bc464`
- Canonical prediction array SHA-256: `56f4b1033d940230e9e02192b50ff510a4e7c72ced9df5db92583cc92c75c285`
- Formats & Range checks: PASSED (single float32 band, EPSG:32611, 100 m, 3730×3292, finite in [0.0, 1.0], NaN outside).
- DrivenData Submission Name: `GEMSDOE35-H35-06-aaa86efb25-20261004T225420098147Z`
- DrivenData Note: `GEMSDOE35 H35-06 scarp-curvature LHS h35-06-aaa86efb25; proxy gate passed; owner mirror unverified; not organizer-scored.`

Report: [`reports/h35-06-20261004T225420098147Z-aaa86efb25.json`](../reports/h35-06-20261004T225420098147Z-aaa86efb25.json). LHS design CSV: [`reports/h35-06-20261004T225420098147Z-aaa86efb25-design.csv`](../reports/h35-06-20261004T225420098147Z-aaa86efb25-design.csv). Format receipt: [`reports/h35-06-submission-validation.json`](../reports/h35-06-submission-validation.json).

