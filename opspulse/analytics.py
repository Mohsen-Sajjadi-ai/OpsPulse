"""Business KPI calculations for CRM and sales operations."""
from __future__ import annotations

import pandas as pd


class OperationsAnalyzer:
    """Calculate transparent, reproducible operational KPIs."""

    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data.copy()
        if self.data.empty:
            raise ValueError("Cannot analyze an empty dataset.")

    def summary(self) -> dict[str, float | int]:
        data = self.data
        return {
            "total_leads": int(len(data)),
            "converted_leads": int(data["converted"].sum()),
            "conversion_rate": float(data["converted"].mean()),
            "average_response_time_hours": float(data["response_time_hours"].mean()),
            "median_response_time_hours": float(data["response_time_hours"].median()),
            "average_interactions": float(data["interactions_count"].mean()),
            "total_pipeline_value_usd": float(data["deal_value_usd"].sum()),
            "converted_pipeline_value_usd": float(
                data.loc[data["converted"] == 1, "deal_value_usd"].sum()
            ),
        }

    def performance_by_source(self) -> pd.DataFrame:
        result = (
            self.data.groupby("lead_source", dropna=False)
            .agg(
                leads=("lead_id", "count"),
                converted_leads=("converted", "sum"),
                conversion_rate=("converted", "mean"),
                avg_response_hours=("response_time_hours", "mean"),
                pipeline_value_usd=("deal_value_usd", "sum"),
            )
            .reset_index()
            .sort_values(["conversion_rate", "leads"], ascending=[False, False])
        )
        return result

    def funnel_by_stage(self) -> pd.DataFrame:
        ordered_stages = ["New", "Qualified", "Proposal", "Closed Won", "Closed Lost"]
        result = (
            self.data.groupby("sales_stage").agg(leads=("lead_id", "count")).reindex(ordered_stages)
            .fillna(0).astype({"leads": "int64"}).reset_index()
        )
        return result.rename(columns={"index": "sales_stage"})

    def key_insights(self) -> list[str]:
        """Create concise observations from measured KPIs (not causal claims)."""
        source = self.performance_by_source()
        region = self.performance_by_region()
        fastest = source.sort_values("avg_response_hours").iloc[0]
        largest_pipeline = source.sort_values("pipeline_value_usd", ascending=False).iloc[0]
        best_conversion = source.sort_values("conversion_rate", ascending=False).iloc[0]
        best_region = region.sort_values("conversion_rate", ascending=False).iloc[0]
        return [
            (f"{best_conversion['lead_source']} had the highest observed conversion rate "
             f"({best_conversion['conversion_rate']:.1%}) across {int(best_conversion['leads'])} leads."),
            (f"{fastest['lead_source']} had the shortest average first-response time "
             f"({fastest['avg_response_hours']:.1f} hours)."),
            (f"{largest_pipeline['lead_source']} represented the largest total pipeline value "
             f"(${largest_pipeline['pipeline_value_usd']:,.0f})."),
            (f"{best_region['region']} had the highest observed regional conversion rate "
             f"({best_region['conversion_rate']:.1%}) across {int(best_region['leads'])} leads."),
        ]

    def performance_by_region(self) -> pd.DataFrame:
        return (
            self.data.groupby("region")
            .agg(
                leads=("lead_id", "count"),
                conversion_rate=("converted", "mean"),
                avg_response_hours=("response_time_hours", "mean"),
            )
            .reset_index()
            .sort_values("conversion_rate", ascending=False)
        )
