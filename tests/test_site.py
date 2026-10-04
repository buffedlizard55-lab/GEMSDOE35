from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

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


def test_site_hero_points_to_current_unique_tiff():
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    filename = "gemsdoe35-h35-01-e58e5dbee6-20261004T164802Z-candidate.tif"
    assert f'downloads/{filename}' in html
    assert (DOCS / "downloads" / filename).is_file()
    assert "not organizer-scored" in html


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
    index_html = (DOCS / "index.html").read_text(encoding="utf-8")
    executive_html = (DOCS / "executive-summary.html").read_text(encoding="utf-8")
    assert "0.3262" in index_html
    assert "owner-maintained" in index_html
    assert "Generative AI" in executive_html
    assert "three submissions per week" in executive_html
