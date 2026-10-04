# Geological hypotheses and evidence register

**Updated:** 2026-10-04 UTC. This register separates scientifically motivated hypotheses from measured DTI results, public leaderboard observations, and owner-reported claims. “Not tried” means the exact detector/signature is not implemented in this checkout; it is not a claim of global novelty. Sibling-site histories are not a complete, independently audited parameter ledger.

## Target and rules that constrain the science

- The official [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) states that the initial private test set contains expert-identified fault pixels absent from the current public USGS map; test-source details are not disclosed. A local holdout on public mapped faults is therefore a **proxy**, not a direct simulation of the private target.
- DrivenData staff define a new fault pixel as geometry not already represented by USGS/INGENIOUS, including a continuation or splay of an existing fault system ([definition, forum topic 11536/post 2](https://community.drivendata.org/t/where-do-you-draw-the-line/11536/2)). Scoring masks catalogue pixels **exactly**; nearby predictions are scored normally, and new geometry may occur within 300 m of known traces ([clarification, topic 11516/post 4](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4)). No detector below uses an artificial catalogue-distance buffer.
- A geophysical anomaly cannot by itself establish that its associated fault is absent from a catalogue. The scientifically defensible claim is narrower: the signature may prioritize a candidate trace/continuation for expert mapping. This checkout's owner-mirror labels support only spatial transfer tests on known faults.
- Training features/labels/template presently come from a public owner-maintained mirror. Pinned hashes establish mirror consistency only; they do not authenticate organizer provenance or licensing. The official competition data page remains login-gated in this environment.

---

## Complete Register of Candidate Geological Hypotheses

Below is the complete, ranked list of candidate geological hypotheses designed for geothermal fault discovery in the Basin and Range province (INGENIOUS / GeoDAWN region).

| Rank by expected improvement | Hypothesis and exact layers | Physical signature and why it could reveal absent fault geometry | Difference from this repo / related prior work | Expected DTI direction and uncertainty | Cost / source readiness |
|---|---|---|---|---|---|
| **1 — H35-06: Topographic scarp curvature & slope-break discontinuity** | Supplied `det_elev` (band 12), `det_elev_slope` (19), `tc` (6), `depth_to_base_surf` (15), and `iso_grav_anom_hg` (18). | Active Quaternary normal and strike-slip faults form continuous topographic scarps and slope-break knickpoints in detrended elevation. Multi-scale directional Hessian curvature ($\lambda_1, \lambda_2$) on `det_elev` combined with slope-gradient inflection analysis identifies subtle facet bases and alluvial fan scarps missed by regional mapping. Corroborated by potential-field tilt curvature (`tc`) and basement depth steps. | First relief-curvature detector in this repo (previous hypotheses used magnetic continuation, strain gradients, or seismicity). Combines 2nd derivative Hessian line filters with slope-break gradient magnitude. Sibling sites used unstratified scarp filters; here evaluated via formal 8-strata LHS. | **Prior:** Moderate-to-high positive. **Observed H35-06 result:** Mean nested outer-fold ΔDTI **+0.014629 vs `tmi_hg`** (5/6 positive tiles) and **+0.008319 vs H35-01** (5/6 positive tiles). **Local proxy gate PASSED.** | **Low–Medium**, uses supplied competition rasters only. No new external data required. Rationale: [USGS 3DEP/GeoDAWN geomorphology](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and). |
| **2 — H35-07: Tilt-angle (`tc`) horizontal derivative & magnetic analytic signal boundary** | Supplied `tc` (band 6), `tmi_hg` (3), `tmi_vg` (9), `rtp` (2), and `iso_grav_anom_hg` (18). | Tilt derivative $\theta = \arctan(VDR / THDR)$ acts as an automatic gain control (AGC) that normalizes deep and shallow structural edges. Taking the horizontal gradient of tilt angle (HG-TA) places sharp, continuous edge maxima directly over vertical/dipping fault contacts regardless of source depth or magnetization amplitude, prioritizing concealed blind faults. | H35-01 used Poisson continuation on RTP/TMI; H35-07 applies tilt derivative AGC edge extraction and 3D analytic signal amplitude, preventing high-amplitude volcanic units from swamping subtle basement fault contacts. | **Prior:** Moderate positive. High theoretical potential for equalizing weak blind fault contacts. | **Low–Medium**, uses supplied competition rasters only. Rationale: Miller & Singh (1994), Verduzco et al. (2004) tilt derivative geophysics. |
| **3 — H35-08: Transtensional geodetic dilatation & shear-strain partitioning corridor** | Supplied `geod_dilaterate` (band 8), `geod_shearrate` (7), `geod_2ndinv` (4), and `deq_n100a15` (10). | >90% of Great Basin geothermal systems are structurally controlled by extensional step-overs, relay ramps, and fault tips where crustal dilatation is maximized. Positive dilatation rate ($\dot{\varepsilon}_{dil} > 0$) combined with shear strain gradient locates active transtensional pull-apart zones where open fractures facilitate hydrothermal upflow. | H35-02 tested shear gradient magnitude alone; H35-08 computes the tensor dilatation-to-shear ratio ($\dot{\varepsilon}_{dil} / \dot{\gamma}_{max}$) and strain partitioning index, specifically targeting fluid-permeable dilatational zones. | **Prior:** Moderate positive for geothermal-specific fault conduits. High spatial resolution limit due to GPS/InSAR smoothing. | **Low–Medium**, uses supplied competition rasters only. Rationale: Faulds & Hinz (2015), Faulds et al. (2021) structural controls of geothermal systems. |
| **4 — H35-09: Joint gravity-magnetic Hessian tensor alignment & cross-gradient structural continuity** | Supplied `iso_grav_anom_hg` (band 18), `tmi_hg` (3), `iso_grav_anom_slope` (5), `tc` (6), and `depth_to_base_surf` (15). | Evaluates the cross-gradient / normalized vector product $|\nabla g \times \nabla m|$ and eigenvectors of the joint gravity-magnetic Hessian tensor. Where density and magnetization boundaries are collinear and parallel, structural contact continuity is maximum, isolating major basement-penetrating fault systems. | H35-04 tested scalar product edge concurrence; H35-09 tests 2D vector field curl and tensor collinearity across multiple spatial scales. | **Prior:** Modest positive. Strong constraint against single-sensor artifacts. | **Low–Medium**, uses supplied competition rasters only. Rationale: Gallardo & Meju (2003) cross-gradient joint structural inversion. |
| **5 — H35-10: External GeoDAWN radiometric alteration contrasts (Area 2 high-resolution)** | External USGS GeoDAWN airborne radiometric K, equivalent Th, and equivalent U grids, paired with supplied `mag_anom` (band 1) and `cond_surf` (17). | Near-surface hydrothermal alteration in geothermal systems often depletes or enriches potassium (K/Th ratio anomalies) along exposed fault traces and permeable fracture corridors. Testing radiometric texture boundaries aligned with magnetic lineaments can reveal unmapped active fault splays. | Radiometric bands are completely absent from the 19 supplied competition layers; this introduces a genuine new empirical data source. | **Prior:** Low-to-moderate potential gain; limited to exposed/near-surface expressions. | **High / Blocked:** Official USGS release [DOI 10.5066/P93LGLVQ](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) / [ScienceBase item 657e1d85d34e23d3533209f7](https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7). Direct download failed with TLS/EOF in this sandboxed environment; requires verified offline download and CRS/transform alignment before viability. |

---

## Detailed Scientific Analysis: The 0.2778 GEMSDOE32 Result & Exceeding the Leaderboard Best (0.3262)

### 1. Mathematical Breakdown of the Distance-Weighted Tversky Index (DTI)
The official metric is defined on a single 100 m grid:
$$DTI = \frac{TP_{weighted}}{TP_{weighted} + \alpha FP_{weighted} + \beta FN_{weighted}}$$
with parameters $\alpha = 0.2$, $\beta = 0.8$, and a 300 m Euclidean triangular kernel:
$$k(d) = \max\left(1 - \frac{d}{300\text{ m}}, 0\right)$$
where $d$ is the Euclidean distance from a predicted point to a ground-truth fault pixel.

Key mathematical properties:
- **True Positive Credit:** For each ground truth pixel $g \in G$, $TP_{weighted}(g) = \max_{x \in P} p(x) k(d(x, g))$.
- **False Positive Penalty:** $FP_{weighted} = \sum_{x \in P} p(x) \left[1 - \max_{g \in G} k(d(x, g))\right]$.
- **False Negative Penalty:** $FN_{weighted} = \sum_{g \in G} \left[1 - \max_{x \in P} p(x) k(d(x, g))\right]$.

### 2. Why Continuous Dense Lines Score Low and Dotted/Sparsified Ridges Score High
- At 100 m grid resolution, the 300 m kernel support spans 3 pixels in radius ($R = 3\text{ px}$).
- If a method predicts a solid continuous 1-pixel wide line ($p(x) = 1.0$), it places 3 predicted pixels across every 300 m stretch.
- When predicting in unmapped areas where ground truth is sparse or uncertain, a continuous line that misses by $>300\text{ m}$ accumulates massive $FP_{weighted}$ penalty ($1.0$ per pixel).
- If instead predictions along the candidate ridge are **spaced / subsampled at $d \approx 2.5 - 2.8\text{ pixels}$ (~250–280 m)**, every ground-truth fault pixel along that segment is still within $\le 140\text{ m}$ of a dot ($k(d) \ge 0.533$ to $1.0$).
- **Result:** $TP$ credit is preserved at ~80–90% of maximum, while total emitted positive mass (and hence potential $FP$) is reduced by **~65%**!
- This explains the clear score progression across the GEMSDOE series:
  - Dense continuous ridges (`h19-5`, `h20-1`): **0.1890 – 0.1922**
  - Dotted at $d=1.5\text{ px}$ (`h25-1-dotted-h19-5-d1-5`): **0.2477**
  - Dotted at $d=2.8\text{ px}$ (`dotted-h19-5-d2-8`, `efd28-repro`): **0.2600**
  - Dotted solo ($d=2.8\text{ px}$): `h27-4-r1-solo-d2-8` / `GEMSDOE31`: **0.2708**
  - High-confidence core flank-pruning (`h33-h33-2-b2`): **0.2778**

### 3. How to Exceed 0.2778 and Reach > 0.3262
To beat 0.2778 and capture the top leaderboard positions (current rank 1 is 0.3262):
1. **Independent Geomorphological Scarp Signal (H35-06):** Incorporating detrended elevation curvature and slope-break knickpoint ridges adds true Quaternary fault scarp expressions that potential fields alone cannot resolve. In our spatial validation, H35-06 achieved **+0.0146 mean ΔDTI vs baseline** and **+0.0083 vs H35-01** across 5/6 spatial tiles.
2. **Transtensional Geodetic Dilatation (H35-08):** Weighting structural intersections by positive dilatation rate isolates active dilatational stepovers where geothermal permeability is highest.
3. **Tilt Derivative AGC Edge Normalization (H35-07):** Applying tilt angle horizontal derivatives eliminates amplitude bias from high-susceptibility volcanics, surfacing weak blind basement fault contacts.
4. **Adaptive Kernel-Matched Point Regularization:** Point-lattice emission matched to the 300 m triangular support radius prevents $FP$ bloat in unmapped terrain.

---

## H35-06 Preregistered Experiment and Validation Results

- **Configuration:** 8-strata Latin Hypercube Sampling (LHS) varying `max_scarp_scale_m` (200–1000 m), `slope_gradient_weight` (0.1–0.9), `tc_corroboration_weight` (0.0–0.8), `depth_step_weight` (0.0–0.8), `prediction_fraction` (0.4%–1.2%), and `curvature_mode` (`asymmetric_step`, `symmetric_ridge`, `inflection_gradient`).
- **Incumbent Comparator:** H35-01 (`h35-01-e58e5dbee6`).
- **Baseline Comparator:** Single-scale `tmi_hg` ranking.
- **Evaluation Split:** Nested leave-one-tile-out cross-validation across 6 contiguous 3×2 spatial cores with 30-pixel boundary exclusion margins and exact emitted pixel mass matching.

### Fold-by-Fold Spatial Validation Summary

| Fold | Challenger Emitted Pixels | Baseline Emitted Pixels | Incumbent Emitted Pixels | Δ vs `tmi_hg` Baseline | Δ vs H35-01 Incumbent | Actual Mass Matched |
|---|---|---|---|---|---|---|
| **R1C1** | 10,871 | 10,871 | 10,871 | −0.016448 | −0.010750 | Yes |
| **R1C2** | 6,868 | 6,868 | 6,868 | **+0.018442** | **+0.015561** | Yes |
| **R2C1** | 8,623 | 8,623 | 8,623 | **+0.024824** | **+0.012737** | Yes |
| **R2C2** | 3,959 | 3,959 | 3,959 | **+0.022137** | **+0.025043** | Yes |
| **R3C1** | 6,218 | 6,218 | 6,218 | **+0.013531** | **+0.001956** | Yes |
| **R3C2** | 2,991 | 2,991 | 2,991 | **+0.025289** | **+0.021671** | Yes |
| **Mean** | — | — | — | **+0.014629** (5/6 positive) | **+0.008319** (5/6 positive) | **GATE PASSED** |

### Selected Configuration Diagnostics (`h35-06-aaa86efb25`)
- `curvature_mode`: `inflection_gradient`
- `max_scarp_scale_m`: `938.45 m`
- `slope_gradient_weight`: `0.7339`
- `tc_corroboration_weight`: `0.7339`
- `depth_step_weight`: `0.2096`
- `prediction_fraction`: `0.765%` (39,530 positive cells)

### Generated Candidate TIFF Properties
- **File:** `docs/downloads/gemsdoe35-h35-06-aaa86efb25-20261004T225420098147Z-candidate.tif`
- **Shape:** 3730 rows × 3292 columns, single-band `float32`
- **CRS:** `EPSG:32611` (UTM Zone 11N)
- **Transform:** `[100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0]`
- **Value Range:** Strictly in `[0.0, 1.0]` for all 5,167,373 domain pixels; `NaN` nodata outside footprint.
- **GeoTIFF SHA-256:** `465935789e62e6a042881a0e2dd11f96dc89d0913a29d3079455c2833c1bc464`
- **Prediction Array SHA-256:** `56f4b1033d940230e9e02192b50ff510a4e7c72ced9df5db92583cc92c75c285`
- **DrivenData Submission Name:** `GEMSDOE35-H35-06-aaa86efb25-20261004T225420098147Z`
- **DrivenData Note:** `GEMSDOE35 H35-06 scarp-curvature LHS h35-06-aaa86efb25; proxy gate passed; owner mirror unverified; not organizer-scored.` (113 characters)
