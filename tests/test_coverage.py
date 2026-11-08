import pytest

from swasthya_setu.coverage import calculate_depth_tier, get_coverage


def test_coverage_specific_never_exceeds_total_documents():
    coverage = get_coverage()
    diseases = coverage["diseases"]
    assert len(diseases) == 30

    for disease in diseases:
        docs = disease["documents"]
        specific = disease["specific_documents"]
        assert specific <= docs, (
            f"Disease {disease['id']} has specific={specific} > total_documents={docs}"
        )
        assert disease["chunks"] >= 0
        assert disease["depth"] in {"basic", "good", "deep"}
        assert "has_general_source" in disease
        assert "newest_source_year" in disease
        if docs > 0:
            assert isinstance(disease["newest_source_year"], int)
            assert disease["newest_source_year"] >= 2008


def test_depth_tier_honesty_rules():
    # Basic tier
    assert calculate_depth_tier(chunks=10, unique_docs_count=1, doc_types=["fact_sheet"]) == "basic"
    assert calculate_depth_tier(chunks=29, unique_docs_count=2, doc_types=["fact_sheet", "guideline"]) == "basic"

    # Good tier
    assert calculate_depth_tier(chunks=30, unique_docs_count=1, doc_types=["guideline"]) == "good"
    assert calculate_depth_tier(chunks=150, unique_docs_count=2, doc_types=["fact_sheet", "guideline"]) == "good"

    # Over 150 chunks, but single document or only fact sheet -> must cap at good, never deep!
    assert calculate_depth_tier(chunks=200, unique_docs_count=1, doc_types=["fact_sheet"]) == "good"
    assert calculate_depth_tier(chunks=200, unique_docs_count=1, doc_types=["guideline"]) == "good"
    assert calculate_depth_tier(chunks=300, unique_docs_count=2, doc_types=["fact_sheet", "fact_sheet"]) == "good"

    # Over 150 chunks with multiple documents and at least one non-fact_sheet -> deep
    assert calculate_depth_tier(chunks=200, unique_docs_count=3, doc_types=["fact_sheet", "guideline", "handbook"], specific_docs_count=2, specific_chunks=80) == "deep"

    # Supported ONLY by general handbooks (specific_docs_count == 0) -> must show good, never deep!
    assert calculate_depth_tier(chunks=500, unique_docs_count=5, doc_types=["handbook", "guideline"], specific_docs_count=0) == "good"

    # Supported mainly by general handbooks with only 1 specific fact sheet (<50 specific chunks) -> good, never deep!
    assert calculate_depth_tier(chunks=600, unique_docs_count=6, doc_types=["fact_sheet", "handbook"], specific_docs_count=1, specific_chunks=10) == "good"


def test_tuberculosis_coverage_honest_count():
    coverage = get_coverage()
    tb = next(d for d in coverage["diseases"] if d["id"] == "tuberculosis")
    assert tb["specific_documents"] <= tb["documents"]
    if tb["documents"] == 0:
        pytest.skip("Local raw source files are git-ignored and not present in a clean checkout.")
    assert tb["documents"] >= 4
    assert tb["chunks"] > 50
    assert tb["newest_source_year"] >= 2025
