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
