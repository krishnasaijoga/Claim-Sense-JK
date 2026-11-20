
from pathlib import Path

from scripts.batch_extract import batch_process_firs


def test_fir_batch_preserves_full_data():
    results = batch_process_firs(
        Path("data/sample_claims")
    )

    claim = next(
        r for r in results
        if r["claim_id"] == "CLM-1006"
    )

    assert claim["fir_status"] == "SUCCESS"
    assert claim["data"]["fir_number"] == "AND/2026/1187"
    assert claim["data"]["brief_facts"] is not None
    assert claim["data"]["police_station"] is not None
    assert "fir_status" not in claim["data"]


def test_fir_batch_not_provided():
    results = batch_process_firs(
        Path("data/sample_claims")
    )

    missing_firs = [
        r for r in results
        if r["fir_status"] == "NOT_PROVIDED"
    ]

    assert len(missing_firs) == 16
    assert all(r["data"] is None for r in missing_firs)
