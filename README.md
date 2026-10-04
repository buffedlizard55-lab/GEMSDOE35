# GEMSDOE35 — DOE GEMS Fault-Discovery Experiments & Space-Filling Design

> **Project Charter:** Reread this entire charter and the full prompt preserved below before any substantive project work. Then check [`AGENTS.md`](AGENTS.md), the [hypothesis register](docs/hypotheses.md), and the latest [experiment report](reports/latest.json). Never turn a local proxy result into an unearned DrivenData score claim.

## Mandatory Continuity Reading & User Prompt Preservation

Below is the complete, unabridged project charter and prompt preserved as required:

```text
Review the repo.   
  
MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION. DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION. BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION.  
  
There should be an easy to download submission tif file as described by the prompt. Read the entire prompt.  
  
Prevent the duplication at the design stage with a formal space-filling design. Catching duplicates after the fact helps, but the deeper fix is to stop generating candidates by hunch-naming, since nothing stops two different-sounding names ("dem10-scarp," "ctx-ridge," "dotted-ridge") from landing in the same neighborhood of configuration space. Latin hypercube sampling (McKay, Beckman, and Conover, Technometrics, 1979) is the standard design for exploring a computer experiment's input space efficiently: it's constructed so that, projected onto any single dimension — feature weighting, threshold, spacing, architecture choice — every sampled configuration lands in a distinct stratum, which the original paper shows gives materially lower variance than random or ad hoc sampling of the same size. Before generating the next batch, enumerate the dimensions that actually vary between attempts, draw the next several candidates as a Latin hypercube over that space rather than by hand, and retire a dimension once its effect on holdout DTI is well-estimated. This guarantees, by construction, that upcoming submissions spread through genuinely different ideas instead of revisiting the same region under a new name.  
  
The following sites should serve as a starting point for understanding how to generate TIF submissions. These websites are researched, and tested and have generated TIF submissions. But we need to generate high scoring submissions.  
  
Here are the results from submissions into the competition, separated by ....:  
  
https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html  
gems-submission-20260925T001403Z-7f00890a: 0.1563  
....  
https://buffedlizard55-lab.github.io/6GEMSDOE/  
gems6_hgb88-topk03_33cec71ff0: 0.0286  
....  
https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html  
pindrop-v4-nodes-20260925T152420Z-f347b70daa: 0.1193  
pindrop-v4-discovery-20260925T152423Z-37f9d5b855: 0.0830  
pindrop-v4-ridge-20260925T152422Z-4e03fc9705: 0.1152  
....  
https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html  
gemsdoe2-dual-family-union-20260925T160406Z-f68e590f: 0.1560  
....  
https://buffedlizard55-lab.github.io/GEMSDOE4/  
gems-submission-20260926T163915Z-237f0063: 0.0343  
....  
https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html  
gems-submission-20260926T175114Z-7f00890a: 0.1563  
....  
https://buffedlizard55-lab.github.io/7GEMSDOE/  
lidarscarp-ridge-top2pct-36c3a3f341c8: 0.1461  
....  
https://buffedlizard55-lab.github.io/8GEMSDOE/  
Hedge-v2_submission: 0.1563  
....  
https://buffedlizard55-lab.github.io/GEMSDOE9/docs/index.html  
2314b599: 0.0107  
....  
https://buffedlizard55-lab.github.io/11GEMSDOE/docs/index.html  
gems-structural-area06-v1: 0.0202  
....  
https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html  
r7-nms3-dem10-scarp_0c9199f14e62: 0.1294  
r7-nms3-dem10-scarp_0c9199f14e62_allfinite: 0.1294  
....  
https://buffedlizard55-lab.github.io/15GEMSDOE/docs/index.html  
gems-tso1-20260929T005627Z-conj_alteration_mag: 0.0782  
....  
https://buffedlizard55-lab.github.io/14GEMSDOE/docs/index.html  
GEMS_r5-geom-horse-ensemble_20260929T154852Z_ccbe1de0_site_e96e942f: 0.0020  
....  
https://buffedlizard55-lab.github.io/17GEMSDOE/  
17GEMSDOE_F-ensemble-2pct_20260930T050626Z: 0.0187  
....  
https://buffedlizard55-lab.github.io/18GEMSDOE/  
H19-C_20260930T212401Z_c11e495e: 0.0297  
....  
https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html  
h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894  
h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan: 0.1922  
....  
https://buffedlizard55-lab.github.io/GEMSDOE10/  
h16-continuation-20260927T065521077735Z-3431b83c7c: 0.0461  
h20-dem10-scarp-thin-20260927T155223039488Z-ffc91a1686: 0.0921  
H25-ctx-ridge-20260927T232947704150Z-6452ae1d00: 0.1280  
h28-dotted-ridge-20260928T020256236880Z-6452ae1d00: 0.1839  
....  
https://buffedlizard55-lab.github.io/13GEMSDOE/  
20261001_r13-lattice-s5_v2_nan-outside: 0.0904  
....  
https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html  
h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan: 0.1855  
h18-3a-topo-geophys-x-complexity-prior-20260930-c502dfab-nan: 0.0976  
h18-4-usgs-geologic-map-faults-gap-20260930-aef8f42c-nan: 0.0360  
....  
https://buffedlizard55-lab.github.io/GEMSDOE21/  
h19-4-reference-20260930-691e4dfa: 0.1894  
....  
https://buffedlizard55-lab.github.io/20GEMSDOE/docs/index.html  
h20-1-sarnnpu-powerlaw-pi0363-tilt-wingcrack-20260930-be0e8f6b-nan: 0.1890  
h20-5-continuous-pu-proxy-unverified-20260930-824ce73a-nan: 0.1859  
....  
https://buffedlizard55-lab.github.io/GEMSDOE22/docs/index.html  
h23-a-dti-optimal-emission-6pct-20261002-e2ec4b49-nan: 0.1002  
h23-b-dti-optimal-emission-10pct-20261002-86176698-nan: 0.0748  
....  
https://buffedlizard55-lab.github.io/GEMSDOE23/  
h30-arrangement-matched-habitat-20261002-0d4e02e8-nan: 0.1352  
....  
https://buffedlizard55-lab.github.io/GEMSDOE24/  
h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan: 0.2477  
....  
https://buffedlizard55-lab.github.io/GEMSDOE25/  
dotted-h19-5-d2-8-20261002-e56ea318af89-nan: 0.2600  
....  
https://buffedlizard55-lab.github.io/GEMSDOE26/  
dilcond-oof-v1-20261003-47629f496133-nan: 0.1223  
....  
https://buffedlizard55-lab.github.io/GEMSDOE27/  
topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan: 0.2449  
....  
https://buffedlizard55-lab.github.io/GEMSDOE28/  
h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan: 0.2708  
....  
https://buffedlizard55-lab.github.io/GEMSDOE29/docs/index.html  
efd28-repro-20261003-1cc7dc534d51-nan: 0.2600  
....  
https://buffedlizard55-lab.github.io/GEMSDOE30/  
d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca: 0.2600  
....  
https://buffedlizard55-lab.github.io/GEMSDOE31/docs/  
h27-4-solo-d28-20261004-8acb75e1-nan: 0.2708  
....  
https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html  
h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778  
....  
WE NEED TO STUDY, ANALYZE, AND UNDERSTAND THE HIGHEST SCORE FROM THE GEMDOE SITE: 0.2778. Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.2778? Answer using PhD level experience, knowledge, and judgment. Current leaderboard leader is 0.3262 (top 3: 0.3262, 0.3222, 0.3195).  
Generate 3–5 candidate geological hypotheses we haven't tried yet, each naming layers, physical signature, why missing from USGS/INGENIOUS, differences from this repo, expected DTI improvement, implementation cost, and free official sources. Validate the top candidate on spatially-blocked holdout before touching a submission slot.  
Ensure GeoTIFF predicted values are strictly in range [0, 1]. Provide an easy 1-click download from the GitHub Pages site and executive summary.
```

---

## Current Artifact — Unique Promoted Candidate H35-06 (Gate PASSED)

**[⬇ Download the Verified H35-06 Candidate GeoTIFF](docs/downloads/gemsdoe35-h35-06-aaa86efb25-20261004T225420098147Z-candidate.tif)** · [Executive Summary and Upload Guide](docs/executive-summary.html) · [Project Site](docs/index.html)

- **Filename:** `gemsdoe35-h35-06-aaa86efb25-20261004T225420098147Z-candidate.tif`
- **DrivenData Submission Name:** `GEMSDOE35-H35-06-aaa86efb25-20261004T225420098147Z`
- **DrivenData Note (&le;200 chars):** `GEMSDOE35 H35-06 scarp-curvature LHS h35-06-aaa86efb25; proxy gate passed; owner mirror unverified; not organizer-scored.` (113 chars)
- **Technical Format:** Single-band `float32`, shape 3,730 × 3,292, CRS `EPSG:32611`, 100 m pixel size, NaN nodata outside domain.
- **Value Range:** **Strictly [0.0, 1.0]** on all 5,167,373 domain pixels (39,530 positive cells, 0.765% emission fraction).
- **GeoTIFF SHA-256:** `465935789e62e6a042881a0e2dd11f96dc89d0913a29d3079455c2833c1bc464`
- **Prediction Array SHA-256:** `56f4b1033d940230e9e02192b50ff510a4e7c72ced9df5db92583cc92c75c285`
- **Local Proxy Gate:** **PASSED** across 5/6 spatial tiles:
  - **Mean ΔDTI vs single-scale `tmi_hg` baseline:** **+0.014629** (5/6 positive outer folds)
  - **Mean ΔDTI vs H35-01 incumbent:** **+0.008319** (5/6 positive outer folds)
  - Exact matched emitted pixel mass across all comparison arms in all 6 folds.

---

## Scientific Analysis of Historical Scores (0.2778) & Strategy to Exceed 0.3262

### 1. Distance-Weighted Tversky Index (DTI) Mathematical Structure
The competition evaluates predictions on a 100 m grid via:
$$DTI = \frac{TP_{weighted}}{TP_{weighted} + \alpha FP_{weighted} + \beta FN_{weighted}} \quad (\alpha = 0.2, \beta = 0.8)$$
using a 300 m Euclidean triangular kernel $k(d) = \max(1 - d/300\text{ m}, 0)$ where 300 m spans 3 pixels ($R = 3\text{ px}$).

- **True Positive Credit:** $TP_{weighted}(g) = \max_{x \in P} p(x) k(d(x,g))$ for each ground-truth pixel $g$.
- **False Positive Penalty:** $FP_{weighted} = \sum_{x \in P} p(x) [1 - \max_g k(d(x,g))]$.

### 2. Why Continuous Lines Fail and Dotted/Pruned Ridges Score High
- Continuous 100 m solid raster lines ($p(x)=1.0$) place 3 pixels across every 300 m span. When predicting in unmapped areas, continuous lines that miss targets by $>300$ m incur massive $FP$ accumulation.
- In contrast, a **spatial sub-Nyquist point lattice ($d \approx 2.5 - 2.8\text{ px}$, ~250–280 m)** places points just under the 300 m capture radius. Every ground truth pixel along a fault is within $\le 140$ m of a predicted dot ($k(d) \ge 0.533$ to $1.0$), capturing ~85% of $TP$ credit while reducing total emitted positive mass by **~65%**, slashing false-positive penalties.
- In GEMSDOE32, H33-2-B2 achieved **0.2778** by combining dotted ridge structures with flank pruning that eliminated diffuse low-confidence boundary noise.

### 3. Concrete Strategy to Exceed 0.2778 and Reach > 0.3262
1. **Multi-Scale Topographic Scarp Inflection (H35-06):** Capturing Quaternary fault scarps, triangular facet bases, and slope breaks in `det_elev` and `det_elev_slope` adds an independent physical lineament channel that beat both baseline and incumbent across 5/6 spatial holdout folds.
2. **Transtensional Geodetic Dilatation (H35-08):** Incorporating positive volumetric strain rate ($\dot{\varepsilon}_{dil} > 0$) isolates permeable extensional step-overs and fault tips where blind geothermal upflow occurs.
3. **Tilt Derivative AGC Edge Normalization (H35-07):** Applying horizontal gradients of tilt angle (`tc`) normalizes deep and shallow structural boundaries, surfacing weak blind fault contacts.
4. **Adaptive Kernel-Matched Point Regularization:** Point-lattice emission matched to the 300 m triangular support radius.

---

## Complete Hypothesis Register (Ranked 1 to 5)

| Rank | Hypothesis | Key Layers | Physical Mechanism & Target | Status & Result |
|---|---|---|---|---|
| **1** | **H35-06: Topographic Scarp Curvature & Slope-Break Discontinuity** | `det_elev`, `det_elev_slope`, `tc`, `depth_to_base_surf`, `iso_grav_anom_hg` | Multi-scale Hessian curvature on detrended relief and slope-break gradient magnitude targeting Quaternary facet bases and fault scarps. | **GATE PASSED:** +0.0146 Δ vs baseline, +0.0083 Δ vs H35-01 (5/6 positive folds). |
| **2** | **H35-07: Tilt Derivative (`tc`) Horizontal Gradient & Analytic Signal** | `tc`, `tmi_hg`, `tmi_vg`, `rtp`, `iso_grav_anom_hg` | Automatic Gain Control (AGC) edge detection on tilt angle normalizing weak blind fault contacts and high-amplitude volcanic contacts. | Queued for LHS screening. |
| **3** | **H35-08: Transtensional Geodetic Dilatation & Shear Corridor** | `geod_dilaterate`, `geod_shearrate`, `geod_2ndinv`, `deq_n100a15` | Dilatation-to-shear ratio ($\dot{\varepsilon}_{dil} / \dot{\gamma}_{max}$) targeting dilatational step-overs and permeable geothermal fluid conduits. | Queued. |
| **4** | **H35-09: Joint Gravity-Magnetic Hessian Tensor & Cross-Gradient Alignment** | `iso_grav_anom_hg`, `tmi_hg`, `iso_grav_anom_slope`, `tc` | Cross-gradient vector product $|\nabla g \times \nabla m|$ and joint tensor eigenvectors ensuring deep structural contact continuity. | Queued. |
| **5** | **H35-10: External GeoDAWN High-Resolution Radiometric Alteration Ratios** | External GeoDAWN K, eTh, eU channels paired with supplied `mag_anom`, `cond_surf` | K/eTh ratio contrasts mapping hydrothermal alteration along surface fault traces. | Blocked on external data audit. |

---

## Resolution of "Predicted values must be in range [0, 1]"

DrivenData enforces strict bounds $[0.0, 1.0]$ on all finite in-footprint pixels. The common error occurs when:
1. Unnormalized gradient/curvature scores ($> 1.0$) are written directly.
2. Raw float subtraction produces small negative values ($< 0.0$).
3. Raw GeoTIFF nodata sentinels (e.g. $-3.4 \times 10^{38}$) bleed into prediction arrays.

**GEMSDOE35 Prevention:**
- All in-domain prediction values are normalized via robust quantile scaling and top-$k$ binary ranking strictly into $[0.0, 1.0]$.
- Outside-domain cells are encoded as IEEE `NaN` nodata.
- Every exported TIFF is automatically reopened and audited by `scripts/validate_submission.py`.

---

## Core Values

- **Maximize P(Win):** Prioritize falsifiable geological hypotheses, space-filling Latin hypercube designs, and measured holdout gains; never spend a competition slot on an unverified or losing candidate.
- **Own the Outcome:** Maintain complete provenance, configuration checksums, full audit trails, and strict honesty about proxy limitations.
