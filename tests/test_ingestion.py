from swasthya_setu.ingestion.loader import normalize_page_text


def test_pdf_normalization_removes_glued_phrase_examples():
    text = normalize_page_text(
        "Symptoms caninclude fever.\n"
        "Retro-orbitalpain may occur.\n"
        "malnutritionare risk factors.\n"
        "42\n"
    )
    assert "caninclude" not in text
    assert "Retro-orbitalpain" not in text
    assert "malnutritionare" not in text
    assert "can include" in text
    assert "retro-orbital pain" in text.lower()
    assert "malnutrition are" in text


def test_ocr_metadata_flag_and_mock(monkeypatch, tmp_path):
    import pymupdf as fitz
    from swasthya_setu.ingestion.loader import load_pdf_paths
    from swasthya_setu.config import settings

    # Create a tiny 1-page blank PDF in tmp_path
    tmp_pdf = tmp_path / "test_blank.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(tmp_pdf))
    doc.close()

    # Disabled by default
    monkeypatch.setattr(settings, "enable_ocr", False)
    monkeypatch.delenv("SWASTHYA_ENABLE_OCR", raising=False)
    docs_no_ocr = load_pdf_paths([tmp_pdf])
    assert len(docs_no_ocr) == 1
    assert docs_no_ocr[0].metadata.get("ocr") is False

    # Enabled with mocked RapidOCR returning text
    class FakeRapidOCR:
        def __call__(self, img_bytes):
            return [[None, "Mocked OCR Extracted Guideline Text"]], None

    monkeypatch.setattr(settings, "enable_ocr", True)
    monkeypatch.setattr("swasthya_setu.ingestion.loader._ocr_empty_pages", lambda pdf, pages: (["Mocked OCR Extracted Guideline Text"], {0}))
    docs_ocr = load_pdf_paths([tmp_pdf])
    assert len(docs_ocr) == 1
    assert docs_ocr[0].metadata.get("ocr") is True
    assert "Mocked OCR Extracted" in docs_ocr[0].page_content

