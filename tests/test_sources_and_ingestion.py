from pathlib import Path

import pytest

from swasthya_setu.ingestion.html_loader import extract_html_text
from swasthya_setu.ingestion.loader import normalize_page_text


def test_html_extractor_drops_navigation_and_keeps_article_text():
    heading, text = extract_html_text(
        "<html><nav>Menu cookie</nav><main><h1>Dengue</h1>"
        "<p>Fever and warning signs.</p></main><footer>Copyright</footer></html>"
    )
    assert heading == "Dengue"
    assert "Fever and warning signs." in text
    assert "Menu" not in text
    assert "Copyright" not in text


def test_html_extractor_who_fixture_page():
    fixture_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Diabetes - WHO</title></head>
    <body>
      <header>
        <div class="sf-header">
          <nav>
            <a href="/newsroom">Newsroom</a>
            <a href="/emergencies">Emergencies</a>
            <a href="/don">Disease Outbreak News</a>
          </nav>
          <div class="language-selector">Select language</div>
        </div>
      </header>
      <div class="cookie-banner">This site uses cookies.</div>
      <article class="sf-detail-body-wrapper">
        <h1>Diabetes</h1>
        <div class="credits">Reading time: 3 mins</div>
        <h2>Key facts</h2>
        <p>Diabetes is a chronic disease that occurs either when the pancreas does not produce enough insulin.</p>
        <h2>Symptoms</h2>
        <p>Symptoms include feeling more thirsty, needing to urinate more often, and blurred vision.</p>
        <h2>WHO response</h2>
        <p>WHO works with Member States to improve diabetes prevention and treatment.</p>
        <h2>References</h2>
        <p>1. Global report on diabetes. Geneva: World Health Organization; 2016.</p>
      </article>
      <footer>
        <p>&copy; 2026 World Health Organization</p>
      </footer>
    </body>
    </html>
    """
    heading, text = extract_html_text(fixture_html)
    assert heading == "Diabetes"
    assert "Key facts" in text
    assert "Symptoms include feeling more thirsty" in text
    # Verify institutional response and references are dropped
    assert "pancreas does not produce enough insulin" in text
    assert "WHO works with Member States" not in text
    assert "Global report on diabetes" not in text
    # Verify forbidden boilerplate strings are strictly absent
    for forbidden in ["Newsroom", "Select language", "Emergencies", "Disease Outbreak News", "Member States", "cookie"]:
        assert forbidden.lower() not in text.lower(), f"Forbidden string '{forbidden}' found in extracted text"


def test_html_extractor_drops_scripts_styles_and_tracking_code():
    html_with_scripts = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Cholera - WHO</title>
      <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime()});})(window,document,'script','dataLayer','GTM-XXXX');</script>
      <script src="https://www.googletagmanager.com/gtm.js?id=GTM-XXXX"></script>
      <style>body { font-family: sans-serif; } .header { color: red; }</style>
    </head>
    <body>
      <noscript><iframe src="https://www.googletagmanager.com/ns.html"></iframe></noscript>
      <script>
        function deleteCookie(name) { window.document.cookie = name + '=; Max-Age=-99999999;'; }
        window.TrackingConsentManager = { getConsent: function() { return true; } };
      </script>
      <main>
        <h1>Cholera</h1>
        <p>Cholera is an acute diarrhoeal infection caused by ingestion of food or water contaminated with the bacterium Vibrio cholerae.</p>
      </main>
    </body>
    </html>
    """
    heading, text = extract_html_text(html_with_scripts)
    assert heading == "Cholera"
    assert "Vibrio cholerae" in text

    for term in [
        "googletagmanager",
        "gtm.js",
        "dataLayer",
        "deleteCookie",
        "TrackingConsentManager",
        "function(",
        "window.",
        "<script",
    ]:
        assert term.lower() not in text.lower(), f"Tracking/script term '{term}' leaked into extracted text"


def test_local_source_files_are_present():
    dengue_pdf = Path("data/raw/dengue_guidelines_2023.pdf")
    who_pdf = Path("data/raw/Fact_Sheet_WHD_2014_EN_1629.pdf")
    if not dengue_pdf.exists() or not who_pdf.exists():
        pytest.skip("Local raw source PDFs are git-ignored and not present in a clean checkout.")
    assert dengue_pdf.exists()
    assert who_pdf.exists()


def test_page_normalization_removes_page_number_lines():
    assert normalize_page_text("Page 12\nUseful health text") == "Useful health text"


def test_build_index_shrink_guard(monkeypatch, tmp_path):
    import importlib.util
    import json
    import sys
    from langchain_core.documents import Document

    # Load build_index module dynamically
    spec = importlib.util.spec_from_file_location("build_index", Path(__file__).resolve().parent.parent / "scripts" / "build_index.py")
    build_index = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_index)

    # Create dummy manifest under vectorstore/index-manifest.json
    vs_dir = tmp_path / "vectorstore"
    vs_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = vs_dir / "index-manifest.json"
    manifest_file.write_text(json.dumps({"chunks": 100, "files": []}), encoding="utf-8")

    # Mock ROOT and all_files to point to tmp_path
    monkeypatch.setattr(build_index, "ROOT", tmp_path)
    monkeypatch.setattr(build_index, "all_files", [])
    # Mock prepare_documents and unique_chunks to return only 50 chunks (< 90 threshold)
    dummy_chunks = [Document(page_content="test", metadata={"source_id": "test", "source": "test.pdf"}) for _ in range(50)]
    monkeypatch.setattr(build_index, "prepare_documents", lambda paths: [])
    monkeypatch.setattr(build_index, "unique_chunks", lambda chunks: dummy_chunks)
    monkeypatch.setattr(build_index, "build_index", lambda chunks: None)

    # Calling without --allow-shrink must exit non-zero (SystemExit)
    with pytest.raises(SystemExit) as exc_info:
        build_index.main([])
    assert exc_info.value.code == 1

    # Calling with --allow-shrink must succeed
    build_index.main(["--allow-shrink"])
    new_manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert new_manifest["chunks"] == 50
