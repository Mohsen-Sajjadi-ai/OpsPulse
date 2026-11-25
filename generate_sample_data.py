"""Generate a clearly synthetic CRM dataset for reproducible project demos."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def sigmoid(value: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-value))


def generate(rows: int = 800, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    regions = np.array(["North America", "Europe", "APAC"])
    industries = np.array(["Technology", "Professional Services", "Retail", "Healthcare", "Education"])
    sizes = np.array(["SMB", "Mid-Market", "Enterprise"])
    sources = np.array(["Website", "Referral", "LinkedIn", "Partner", "Webinar", "Paid Search"])

    region = rng.choice(regions, rows, p=[0.38, 0.34, 0.28])
    industry = rng.choice(industries, rows, p=[0.24, 0.21, 0.18, 0.16, 0.21])
    company_size = rng.choice(sizes, rows, p=[0.54, 0.31, 0.15])
    lead_source = rng.choice(sources, rows, p=[0.27, 0.18, 0.16, 0.14, 0.13, 0.12])
    response_time = np.clip(rng.gamma(shape=2.2, scale=7.5, size=rows), 0.2, 96)
    interactions = np.clip(rng.poisson(lam=3.2, size=rows), 0, 18)
    previous_purchases = rng.choice([0, 1, 2, 3], rows, p=[0.66, 0.21, 0.09, 0.04])

    logit = (
        -1.35
        + 0.22 * interactions
        - 0.035 * response_time
        + 0.58 * previous_purchases
        + 0.62 * (lead_source == "Referral")
        + 0.42 * (lead_source == "Partner")
        + 0.35 * (company_size == "Enterprise")
        + 0.20 * (company_size == "Mid-Market")
        + 0.18 * (industry == "Technology")
        + 0.12 * (region == "North America")
        + rng.normal(0, 0.55, rows)
    )
    conversion_probability = sigmoid(logit)
    converted = rng.binomial(1, conversion_probability)

    stage = []
    for outcome, probability in zip(converted, conversion_probability):
        if outcome == 1:
            stage.append("Closed Won")
        else:
            # A small set of open and lost stages creates a useful operational funnel.
            adjusted = np.array([0.34, 0.34, 0.19, 0.13])
            if probability > 0.45:
                adjusted = np.array([0.14, 0.39, 0.34, 0.13])
            stage.append(rng.choice(["New", "Qualified", "Proposal", "Closed Lost"], p=adjusted))

    size_multiplier = pd.Series(company_size).map({"SMB": 1.0, "Mid-Market": 3.0, "Enterprise": 8.0}).to_numpy()
    deal_value = np.round(rng.uniform(800, 8500, rows) * size_multiplier, 2)
    dates = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 620, rows), unit="D")

    return pd.DataFrame({
        "lead_id": [f"LD-{i:05d}" for i in range(1, rows + 1)],
        "created_at": dates.strftime("%Y-%m-%d"),
        "region": region,
        "industry": industry,
        "company_size": company_size,
        "lead_source": lead_source,
        "response_time_hours": np.round(response_time, 2),
        "interactions_count": interactions,
        "previous_purchases": previous_purchases,
        "sales_stage": stage,
        "deal_value_usd": deal_value,
        "converted": converted,
    })


if __name__ == "__main__":
    output = Path(__file__).resolve().parent / "sample_data" / "crm_leads.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    generate().to_csv(output, index=False)
    print(f"Generated synthetic CRM dataset: {output}")
