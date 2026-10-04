from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for name in ("href", "src"):
            if attrs.get(name):
                self.urls.append(attrs[name])


def test_site_internal_links_resolve():
    for html_path in (DOCS / "index.html", DOCS / "executive-summary.html"):
        parser = Links()
        parser.feed(html_path.read_text(encoding="utf-8"))
        for url in parser.urls:
            if url.startswith(("#", "http://", "https://", "mailto:", "data:")):
                continue
            target = (html_path.parent / urlparse(url).path).resolve()
            assert target.is_file(), f"broken link in {html_path.name}: {url}"


def test_site_hero_points_to_current_candidate_tiff():
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    filename = "gemsdoe35-h35-06-aaa86efb25-20261004T225420098147Z-candidate.tif"
    assert f'downloads/{filename}' in html
    assert (DOCS / "downloads" / filename).is_file()
    assert "not organizer-scored" in html
    assert "GATE PASSED" in html


def test_pages_root_redirects_to_docs_site_and_summary():
    root_index = (ROOT / "index.html").read_text(encoding="utf-8")
    root_summary = (ROOT / "executive-summary.html").read_text(encoding="utf-8")
    assert "docs/index.html" in root_index
    assert "docs/executive-summary.html" in root_summary


def test_site_visible_evidence_is_current_and_caveated():
    report = DOCS / "evidence/latest-experiment.json"
    validation = DOCS / "evidence/submission-validation.json"
    assert report.is_file()
    assert validation.is_file()
    challenger = DOCS / "evidence/h35-02-latest.json"
    latest_h35_03 = DOCS / "evidence/h35-03-latest.json"
    latest_h35_04 = DOCS / "evidence/h35-04-latest.json"
    h35_04_validation = DOCS / "evidence/h35-04-submission-validation.json"
    latest_h35_05 = DOCS / "evidence/h35-05-latest.json"
    h35_05_validation = DOCS / "evidence/h35-05-submission-validation.json"
    latest_h35_06 = DOCS / "evidence/h35-06-latest.json"
    h35_06_validation = DOCS / "evidence/h35-06-submission-validation.json"
    reconstruction = DOCS / "evidence/candidate-reconstruction.json"
    assert challenger.is_file()
    assert latest_h35_03.is_file()
    assert latest_h35_04.is_file()
    assert h35_04_validation.is_file()
    assert latest_h35_05.is_file()
    assert h35_05_validation.is_file()
    assert latest_h35_06.is_file()
    assert h35_06_validation.is_file()
    assert reconstruction.is_file()
    assert (ROOT / "docs/original-project-prompt.md").is_file()
    index_html = (DOCS / "index.html").read_text(encoding="utf-8")
    executive_html = (DOCS / "executive-summary.html").read_text(encoding="utf-8")
    assert "0.3262" in index_html
    assert "0.2778" in index_html
    assert "H35-06" in index_html
    assert "Topographic Scarp Curvature" in index_html
    assert "GATE PASSED" in index_html
    assert "three feedback submissions per week" in executive_html or "competition" in executive_html
    assert "Generative AI" in executive_html or "generative" in executive_html.lower()

    import json

    challenger_report = json.loads(challenger.read_text(encoding="utf-8"))
    h35_03_report = json.loads(latest_h35_03.read_text(encoding="utf-8"))
    h35_04_report = json.loads(latest_h35_04.read_text(encoding="utf-8"))
    h35_05_report = json.loads(latest_h35_05.read_text(encoding="utf-8"))
    h35_06_report = json.loads(latest_h35_06.read_text(encoding="utf-8"))
    latest_report = json.loads(report.read_text(encoding="utf-8"))
    reconstruction_report = json.loads(reconstruction.read_text(encoding="utf-8"))
    validation_receipt = json.loads(h35_06_validation.read_text(encoding="utf-8"))
    assert h35_03_report["hypothesis_id"] == "H35-03"
    assert h35_03_report["gate"]["passed"] is False
    assert h35_04_report["hypothesis_id"] == "H35-04"
    assert h35_04_report["gate"]["passed"] is False
    assert h35_05_report["hypothesis_id"] == "H35-05"
    assert h35_05_report["gate"]["passed"] is False
    assert h35_06_report["hypothesis_id"] == "H35-06"
    assert h35_06_report["gate"]["passed"] is True
    assert h35_06_report["outer_summary"]["matched_actual_emission_all_outer_folds"] is True
    assert h35_06_report["outer_summary"]["positive_folds_vs_baseline"] == 5
    assert h35_06_report["outer_summary"]["positive_folds_vs_incumbent"] == 5
    assert h35_06_report["outer_summary"]["mean_delta_vs_baseline"] > 0
    assert h35_06_report["outer_summary"]["mean_delta_vs_incumbent"] > 0
    assert h35_06_report["submission"]["positive_pixels"] == 39530
    assert h35_06_report["duplicate_audit"]["unique_within_local_scan"] is True
    assert validation_receipt["range_gate"] == "pass"
    assert validation_receipt["sha256"] == h35_06_report["submission"]["sha256"]
    assert latest_report["hypothesis_id"] == "H35-06"
    assert latest_report["gate"]["passed"] is True
    assert challenger_report["gate"]["passed"] is False
    budget = challenger_report["incumbent_budget_comparison"]
    assert budget["status"] == "matched"
    assert budget["equal_emitted_mass_all_arms"] is True
    assert budget["challenger_emitted_pixels"] == budget["incumbent_emitted_pixels"] == 27979
    superseded = json.loads((ROOT / "reports/h35-02-20261004T175239Z-6882a35675.json").read_text(encoding="utf-8"))
    assert superseded["report_status"].startswith("superseded")
    assert reconstruction_report["status"] == "exact_prediction_reproduction_passed"
