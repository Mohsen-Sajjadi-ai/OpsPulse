import pandas as pd
import pytest

from opspulse.data import CRMDataLoader, DataValidationError


def valid_frame():
    return pd.DataFrame({
        "lead_id": ["A", "B"],
        "created_at": ["2026-01-01", "2026-01-02"],
        "region": ["Europe", "APAC"],
        "industry": ["Technology", "Retail"],
        "company_size": ["SMB", "Enterprise"],
        "lead_source": ["Referral", "Website"],
        "response_time_hours": [2.0, 4.0],
        "interactions_count": [3, 1],
        "previous_purchases": [1, 0],
        "sales_stage": ["Closed Won", "New"],
        "deal_value_usd": [1000.0, 2000.0],
        "converted": [1, 0],
    })


def test_loader_accepts_valid_data(tmp_path):
    path = tmp_path / "valid.csv"
    valid_frame().to_csv(path, index=False)
    loaded = CRMDataLoader().load(path)
    assert len(loaded) == 2
    assert loaded["converted"].tolist() == [1, 0]


def test_loader_rejects_duplicate_ids(tmp_path):
    frame = valid_frame()
    frame.loc[1, "lead_id"] = "A"
    path = tmp_path / "duplicate.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(DataValidationError, match="unique"):
        CRMDataLoader().load(path)


def test_loader_rejects_negative_response_time(tmp_path):
    frame = valid_frame()
    frame.loc[0, "response_time_hours"] = -1
    path = tmp_path / "negative.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(DataValidationError, match="negative"):
        CRMDataLoader().load(path)
