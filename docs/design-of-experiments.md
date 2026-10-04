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

## Other ranked hypotheses (not implemented in this run)

- **H35-04, GeoDAWN radiometric alteration contrast:** external official USGS/DOE data source; the ScienceBase record lists area-specific GeoTIFF archives and Data.gov marks the release public domain. The actual archive has not been downloaded or aligned here; it remains blocked pending file, CRS, target-overlap, and license/rules audit. Its shallow measurement sensitivity means it may help exposed structures but not hidden faults.
- **H35-05, seismicity-density transition:** uses the supplied earthquake-intensity and distance-to-earthquake surfaces, testing spatial gradients/terminations rather than density hotspots. Low–medium implementation cost; broad/smoothed layers and catalog incompleteness are major failure modes.
- **H35-06, depth-connected MT conductance:** USGS ScienceBase lists five approximately 3.94-MB GeoTIFFs and the release is CC0. FGDC metadata describes 1-km cells on a custom Albers grid while the ScienceBase raster extension says EPSG:4269; direct binary retrieval did not succeed from this environment. Do not treat this as viable until file checksums, actual CRS/transform, target overlap and resampling are verified. Even if obtained, 1-km cells cannot provide 100-m trace detail.

## Factor retirement and score interpretation

A factor is not retired because its current LHS has a winner or one range underperformed. Retire it only after replicated, spatially blocked estimates of its main effect and relevant interactions are stable across preregistered ranges, with uncertainty and any data-quality sensitivity logged. H35-02 does not retire all strain features. Keep failures, superseded reports, config CSVs, checksums, source links and caveats. Local spatial scores on existing mapped faults remain separate from organizer-scored public/private/final outcomes.
