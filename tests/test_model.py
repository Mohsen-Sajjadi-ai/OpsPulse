from pathlib import Path
import sys

from generate_sample_data import generate
from opspulse.model import LeadConversionModel


def test_model_evaluates_and_scores():
    data = generate(rows=240, seed=123)
    model = LeadConversionModel(random_state=7)
    metrics = model.evaluate(data)
    assert 0 <= metrics.accuracy <= 1
    assert 0 <= metrics.roc_auc <= 1
    model.fit(data)
    scores = model.score_leads(data)
    assert "conversion_probability" in scores.columns
    assert scores["conversion_probability"].between(0, 1).all()
    assert scores.iloc[0]["conversion_probability"] >= scores.iloc[-1]["conversion_probability"]

def test_model_out_of_fold_scoring():
    data = generate(rows=240, seed=321)
    model = LeadConversionModel(random_state=7)

    scores = model.score_leads_out_of_fold(data, n_splits=5)

    assert len(scores) == len(data)
    assert scores["lead_id"].nunique() == len(data)
    assert scores["conversion_probability"].notna().all()
    assert scores["conversion_probability"].between(0, 1).all()
    assert scores["priority_band"].isin(
        ["Low", "Medium", "High"]
    ).all()

    assert (
        scores.iloc[0]["conversion_probability"]
        >= scores.iloc[-1]["conversion_probability"]
    )