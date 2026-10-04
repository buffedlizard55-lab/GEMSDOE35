# Original Project Prompt and Durable Task Register

> This file preserves the user's complete project intent in an auditable, normalized register. The repeated instructions are consolidated rather than duplicated; the historical score strings below are user-supplied claims unless independently linked to the official DrivenData leaderboard. Read this register together with the README charter before substantive work.

## Mission and non-negotiable outcomes

Review and improve this repository for the DOE GEMS Prize Challenge (DrivenData competition 306). The objective is to build a scientifically grounded, reproducible and useful fault-mapping workflow that maximizes the probability of a strong competition result—not to promise a win. The specific goal is to generate a **unique, single-band GeoTIFF prediction file** that is easy to download and, after careful review, manually submit to DrivenData. Do not copy a previous submission and merely rename it. A candidate is eligible for consideration only after a preregistered spatially blocked evaluation beats the current local holdout incumbent; no competition slot may be spent on an untested or holdout-losing idea.

Explain the reported GEMSDOE32 value of 0.2778, investigate the linked official public leaderboard, and distinguish actual public scores from owner-reported claims, model projections, local holdout results and organizer-scored submissions. Current official sources override stale user-provided snapshots. A higher score is an objective to test, not a result to assert in advance.

Build an auditable knowledge base with scientific and official sources, organized geological hypotheses, explicit data provenance, experiment configurations, holdout results, checksums, known irregularities, and a clear next-step queue. Revisit this brief at the start of each substantive work session. Work autonomously where access permits; do not ask for or store credentials, bypass login controls, fabricate evidence, or conceal uncertainty.

## Historical project pages and score claims supplied by the user

These links and score/name associations were pasted into the initial request. They are research leads and are **not automatically verified organizer scores**. The official leaderboard is the only source for public-board participant values; even that does not establish which local artifact generated a row.

| Project page | User-supplied submission / value |
|---|---|
| [GEMSDOE](https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html) | `gems-submission-20260925T001403Z-7f00890a`: 0.1563 |
| [6GEMSDOE](https://buffedlizard55-lab.github.io/6GEMSDOE/) | `gems6_hgb88-topk03_33cec71ff0`: 0.0286 |
| [GEMSDOE3](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html) | `pindrop-v4-nodes-20260925T152420Z-f347b70daa`: 0.1193; `pindrop-v4-discovery-20260925T152423Z-37f9d5b855`: 0.0830; `pindrop-v4-ridge-20260925T152422Z-4e03fc9705`: 0.1152 |
| [GEMSDOE2](https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html) | `gemsdoe2-dual-family-union-20260925T160406Z-f68e590f`: 0.1560 |
| [GEMSDOE4](https://buffedlizard55-lab.github.io/GEMSDOE4/) | `gems-submission-20260926T163915Z-237f0063`: 0.0343 |
| [5GEMSDOE](https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html) | `gems-submission-20260926T175114Z-7f00890a`: 0.1563 |
| [7GEMSDOE](https://buffedlizard55-lab.github.io/7GEMSDOE/) | `lidarscarp-ridge-top2pct-36c3a3f341c8`: 0.1461 |
| [8GEMSDOE](https://buffedlizard55-lab.github.io/8GEMSDOE/) | `Hedge-v2_submission`: 0.1563 |
| [GEMSDOE9](https://buffedlizard55-lab.github.io/GEMSDOE9/docs/index.html) | `2314b599`: 0.0107 |
| [11GEMSDOE](https://buffedlizard55-lab.github.io/11GEMSDOE/docs/index.html) | `gems-structural-area06-v1`: 0.0202 |
| [12GEMSDOE](https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html) | `r7-nms3-dem10-scarp_0c9199f14e62`: 0.1294; `_allfinite`: 0.1294 |
| [15GEMSDOE](https://buffedlizard55-lab.github.io/15GEMSDOE/docs/index.html) | `gems-tso1-20260929T005627Z-conj_alteration_mag`: 0.0782 |
| [14GEMSDOE](https://buffedlizard55-lab.github.io/14GEMSDOE/docs/index.html) | `GEMS_r5-geom-horse-ensemble_20260929T154852Z_ccbe1de0_site_e96e942f`: 0.0020 |
| [17GEMSDOE](https://buffedlizard55-lab.github.io/17GEMSDOE/) | `17GEMSDOE_F-ensemble-2pct_20260930T050626Z`: 0.0187 |
| [18GEMSDOE](https://buffedlizard55-lab.github.io/18GEMSDOE/) | `H19-C_20260930T212401Z_c11e495e`: 0.0297 |
| [19GEMSDOE](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html) | `h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan`: 0.1894; `h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan`: 0.1922 |
| [GEMSDOE10](https://buffedlizard55-lab.github.io/GEMSDOE10/) | `h16-continuation-20260927T065521077735Z-3431b83c7c`: 0.0461; `h20-dem10-scarp-thin-20260927T155223039488Z-ffc91a1686`: 0.0921; `H25-ctx-ridge-20260927T232947704150Z-6452ae1d00`: 0.1280; `h28-dotted-ridge-20260928T020256236880Z-6452ae1d00`: 0.1839 |
| [13GEMSDOE](https://buffedlizard55-lab.github.io/13GEMSDOE/) | `20261001_r13-lattice-s5_v2_nan-outside`: 0.0904 |
| [16GEMSDOE](https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html) | `h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan`: 0.1855; `h18-3a-topo-geophys-x-complexity-prior-20260930-c502dfab-nan`: 0.0976; `h18-4-usgs-geologic-map-faults-gap-20260930-aef8f42c-nan`: 0.0360 |
| [GEMSDOE21](https://buffedlizard55-lab.github.io/GEMSDOE21/) | `h19-4-reference-20260930-691e4dfa`: 0.1894 |
| [20GEMSDOE](https://buffedlizard55-lab.github.io/20GEMSDOE/docs/index.html) | `h20-1-sarnnpu-powerlaw-pi0363-tilt-wingcrack-20260930-be0e8f6b-nan`: 0.1890; `h20-5-continuous-pu-proxy-unverified-20260930-824ce73a-nan`: 0.1859 |
| [GEMSDOE22](https://buffedlizard55-lab.github.io/GEMSDOE22/docs/index.html) | `h23-a-dti-optimal-emission-6pct-20261002-e2ec4b49-nan`: 0.1002; `h23-b-dti-optimal-emission-10pct-20261002-86176698-nan`: 0.0748 |
| [GEMSDOE23](https://buffedlizard55-lab.github.io/GEMSDOE23/) | `h30-arrangement-matched-habitat-20261002-0d4e02e8-nan`: 0.1352 |
| [GEMSDOE24](https://buffedlizard55-lab.github.io/GEMSDOE24/) | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan`: 0.2477 |
| [GEMSDOE25](https://buffedlizard55-lab.github.io/GEMSDOE25/) | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan`: 0.2600 |
| [GEMSDOE26](https://buffedlizard55-lab.github.io/GEMSDOE26/) | `dilcond-oof-v1-20261003-47629f496133-nan`: 0.1223 |
| [GEMSDOE27](https://buffedlizard55-lab.github.io/GEMSDOE27/) | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan`: 0.2449 |
| [GEMSDOE28](https://buffedlizard55-lab.github.io/GEMSDOE28/) | `h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan`: 0.2708; `h32-1-prethin-tip-euler-d2-8-20261003-31e35eee884e-nan`, `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan`, `h38-1-hf-euler-r30-r1-20261003-56a9f473edc7-nan` supplied without scores |
| [GEMSDOE29](https://buffedlizard55-lab.github.io/GEMSDOE29/docs/index.html) | `efd28-repro-20261003-1cc7dc534d51-nan`: 0.2600; `repo-c0-habitat-emission-20261003-a4d439b07426-nan`, `sgmc-off-catalogue-44k-20261003-c8dcd780e3fd-nan`, `wormrank-d28-20261003-59dcaf6dd11d-zeros`, `wormsurv-filter-20261003-921f10960d6e-zeros`, `xfit-c0-habitat-20261003-ca879db0089a-zeros`, and `xfit-h41-union-qfaults-20261003-9edb34b99e3a-zeros` supplied without scores |
| [GEMSDOE30](https://buffedlizard55-lab.github.io/GEMSDOE30/) | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca`: 0.2600 |
| [GEMSDOE31](https://buffedlizard55-lab.github.io/GEMSDOE31/docs/) | `h27-4-solo-d28-20261004-8acb75e1-nan`: 0.2708 |
| [GEMSDOE32](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`: user-reported 0.2778; the site itself and owner-maintained PR call the projected 0.2747 a model, not a verified organizer score. The official board snapshot associates 0.2778 with `extradr19`; the file-to-row linkage is unverified. |
| [GEMSDOE33](https://buffedlizard55-lab.github.io/GEMSDOE33/) | No score supplied |

The original message also stated “0.3195 is the highest score right now.” That statement was time-dependent and was already stale in the official 2026-10-04 snapshot: the public leaderboard showed 0.3262 (`nchuzhoy`), 0.3222 (`kinghorton42`), and 0.3195 (`DARD`). Those are public values, not hidden/private or final prize results. See [`docs/evidence/leaderboard-20261004.json`](evidence/leaderboard-20261004.json) and the live [official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).

## Competition task and official references

- Competition: [DOE GEMS Prize](https://www.drivendata.org/competitions/306/competition-doe-gems/), [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/), [data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).
- [DrivenData/NLR official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) and [DrivenData Terms of Use](https://www.drivendata.org/termsofuse/).
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution).
- [NLR GEMS data/report mirror mentioned in the request](https://gdr.openei.org/submissions/1391).
- User-supplied public links for rules/format evidence: [official rules PDF on NLR](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [Dropbox copy of rules PDF](https://www.dropbox.com/scl/fi/aemhtutjgcp6tr3tint94/GEMS_96647.pdf?rlkey=rek210cj2smnmzb8n0sla1vmd&st=wz4kofki&dl=0), [example submission TIFF](https://www.dropbox.com/scl/fi/6rgvnuady818ol8yqgis4/example_submission.tif?rlkey=kbykilvau066xuogoosbf4cq8&st=8junzdyw&dl=0), [existing-faults TIFF](https://www.dropbox.com/scl/fi/t7fyt03qdh9egyme0itwo/existing_faults.tif?rlkey=yiao96uluqdkipf0h5vju71jf&st=rnino7ya&dl=0), [GeoDAWN numerical-feature TIFF](https://www.dropbox.com/scl/fi/3vz9o0wwavi26xaeoxlwr/gems-geodawn-numerical-features.tif?rlkey=je8d8fepqfbst9lnwsq9rkplu&st=zj1lag1r&dl=0), and [DEM links PDF](https://www.dropbox.com/scl/fi/ig0mban712ns1atphgphe/Digital-elevation-model-links-JSON.pdf?rlkey=zm77f1vbtt2if8hlruymptnu3&st=srhhir10&dl=0). These owner/user-provided links are not substituted for official organizer authentication.

The required contest output is one single-band 32-bit float GeoTIFF: EPSG:32611, 100 m resolution, training-area bounds, null/NaN outside the footprint, and prediction/confidence values in `[0,1]`. Upload name and optional note must distinguish the submission. The site must place the download near the top and include a plain-language executive-summary upload walkthrough.

## Research and design instructions

Before implementing a new detector, preregister 3–5 plausible geological hypotheses. For each state the named data layers, physical signature (for example edge, curvature, continuation, orientation or halo), why it could reveal a fault pixel/continuation/splay missing from the USGS/INGENIOUS catalogue, difference from this repository and reported prior work, expected DTI direction without presenting a prior as measured, implementation cost, and any external source. If external data are required, identify an official free source and verify that its files are obtainable before calling the idea viable.

List every factor that varies across attempts. Use a formal design such as a mixed Latin hypercube, with deterministic seed, unique canonical configuration IDs, continuous factor bounds, balanced categorical levels, and all fixed protocol values in the ID. LHS guarantees marginal stratification, not universal interaction coverage or improvement. Retire a dimension only after replicated spatially blocked estimates of its main effect and interactions are sufficiently stable. Preserve failed and invalidated runs; do not hand-name configurations that could be duplicates in feature space.

Validate the selected candidate on spatially blocked data before any competition upload. Distinguish development blocks from held-out blocks, quantify the DTI effect against a declared incumbent at an explicitly described prediction budget, and disclose any reuse of a holdout. A local catalogue-label proxy is not the private newly identified fault population and cannot be converted into a leaderboard score without evidence. No score claim should be made without an organizer result/receipt.

Research the official problem, geology, data provenance, source licensing, metric, submission rules, data quality, and prior approaches. Save accurate claims with official/peer-reviewed links for manual review. Record irregularities and limitations. Be especially careful not to misattribute a public leaderboard row to a local file when there is no verified file-to-submission link.

## Data access, blockers, and no-bypass rule

The official competition data tab is login-walled to an enrolled account. An unauthenticated request redirects to DrivenData login. This session has no authenticated organizer download for `training_features.tif`, `labels.tif`, `sample_submission.tif`, or `1m_DEM_links.csv`. Do not request, store or expose user credentials, automate login, or bypass this access control. Where useful for local engineering tests, a public owner-maintained GitHub mirror may be used only with clear caveats; its own hashes establish mirror integrity, not organizer provenance or licensing.

The original request named the single data-placement blocker and asked to run `bash scripts/download_competition_data.sh` followed by `python scripts/prepare_data.py` on an unrestricted machine. This repository does not bypass authentication; the current audited public-mirror fallback is `python scripts/reassemble_owner_mirror.py`, followed by `python scripts/prepare_data.py`. For verified competition work, use the enrolled account's authorized files and rerun preparation/validation. Training a large U-Net/reference model may benefit from a GPU; the current deterministic H35 feature transforms, metric, holdout scoring and output formatting run on CPU.

External public data must be free, official/peer-reviewed as relevant, have a license compatible with the rules and final shared artifacts, and be source-registered. One candidate source is the [USGS Great Basin electrical-conductance release, DOI 10.5066/P9TWT2LU](https://www.usgs.gov/data/electrical-conductance-maps-great-basin-usa), with files listed in [ScienceBase](https://www.sciencebase.gov/catalog/item/62979746d34ec53d276c113b); its CC0 marking and five depth-slice listings do not by themselves verify the local resolution/alignment needed here.

## Website, upload guide, maintenance and safeguards

The project site should have a simple, accessible, mobile-friendly layout; the unique TIFF download should be an obvious first-visit action; the executive summary should show the file name, submission name, optional note, exact format validation, and numbered manual upload steps. Clearly label local results, public leaderboard snapshots, private/final results, and owner projections as different evidence classes. Never say a candidate has an organizer score unless a receipt verifies it.

The desired project also includes an up-to-date feed to reduce manual checking. However, the official [DrivenData Terms of Use](https://www.drivendata.org/termsofuse/) prohibit using robots/spiders/automatic processes to access the site for monitoring/copying, and prohibit manual monitoring/copying without prior written consent. Therefore a scheduled leaderboard scraper is not acceptable. Until DrivenData grants written permission or an approved API/feed exists, publish a date-stamped, manually reviewed snapshot and explain this blocker. Public official sources such as USGS APIs may be checked only within their own published terms.

Run three explicit passes on each substantial delivery: (1) implement and verify; (2) review for bugs, omissions, assumptions and edge cases, then fix; (3) recheck every requirement in this prompt and improve accuracy/reliability. Provide limitations and next steps. If GitHub permissions allow, open a pull request from the Arena-tracked session branch and merge it only after tests/review; never switch off the session branch.

## Arena Core Values

- **Maximize P(Win):** in every choice weigh risk and evidence, prioritize falsifiable hypotheses, designed experiments, spatially blocked validation, and scarce slot discipline over novelty-by-name or optimistic projections.
- **Own the Outcome:** own the full result end to end. Keep data provenance, exact configs, failed runs, code, tests, source links, checksums and limitations visible. Treat failures as signal. Do not overstate a win.
