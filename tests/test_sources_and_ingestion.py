from pathlib import Path

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


def test_local_source_files_are_present():
    assert Path("data/raw/dengue_guidelines_2023.pdf").exists()
    assert Path("data/raw/Fact_Sheet_WHD_2014_EN_1629.pdf").exists()


def test_page_normalization_removes_page_number_lines():
    assert normalize_page_text("Page 12\nUseful health text") == "Useful health text"
