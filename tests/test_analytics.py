import pandas as pd

from opspulse.analytics import OperationsAnalyzer


def test_summary_and_source_metrics():
    frame = pd.DataFrame({
        "lead_id": ["A", "B", "C"],
        "converted": [1, 0, 1],
        "response_time_hours": [2.0, 4.0, 6.0],
        "interactions_count": [3, 1, 4],
        "deal_value_usd": [1000.0, 2000.0, 3000.0],
        "lead_source": ["Referral", "Website", "Referral"],
        "sales_stage": ["Closed Won", "New", "Closed Won"],
        "region": ["Europe", "APAC", "Europe"],
    })
    analyzer = OperationsAnalyzer(frame)
    summary = analyzer.summary()
    assert summary["total_leads"] == 3
    assert summary["converted_leads"] == 2
    assert summary["conversion_rate"] == 2 / 3
    source = analyzer.performance_by_source()
    referral = source.loc[source["lead_source"] == "Referral"].iloc[0]
    assert referral["leads"] == 2
    assert referral["conversion_rate"] == 1.0
