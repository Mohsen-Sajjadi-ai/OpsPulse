"""Build a portable report bundle from OpsPulse analysis outputs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from .analytics import OperationsAnalyzer
from .charts import DashboardCharts
from .model import LeadConversionModel
from .storage import SQLiteStore


class ReportBuilder:
    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _write_json(payload: dict[str, Any], path: Path) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def build(
        self,
        data: pd.DataFrame,
        model: LeadConversionModel,
        model_evaluation: dict[str, Any],
        quality_report: dict[str, Any] | None = None,
    ) -> dict[str, Path]:
        analyzer = OperationsAnalyzer(data)
        summary = analyzer.summary()
        source_metrics = analyzer.performance_by_source()
        funnel = analyzer.funnel_by_stage()
        region_metrics = analyzer.performance_by_region()
        scored = model.score_leads_out_of_fold(data)
        coefficient_table = model.coefficient_table()

        summary_path = self.output_dir / "kpi_summary.json"
        source_path = self.output_dir / "source_performance.csv"
        funnel_path = self.output_dir / "sales_funnel.csv"
        region_path = self.output_dir / "region_performance.csv"
        scored_path = self.output_dir / "lead_scores.csv"
        model_metrics_path = self.output_dir / "model_evaluation.json"
        database_path = self.output_dir / "opspulse.sqlite"
        model_path = self.output_dir / "lead_conversion_model.joblib"
        coefficients_path = self.output_dir / "model_coefficients.csv"
        insights_path = self.output_dir / "key_insights.json"
        quality_path = self.output_dir / "data_quality_report.json"

        self._write_json(summary, summary_path)
        self._write_json(model_evaluation, model_metrics_path)
        source_metrics.to_csv(source_path, index=False)
        funnel.to_csv(funnel_path, index=False)
        region_metrics.to_csv(region_path, index=False)
        scored.to_csv(scored_path, index=False)
        coefficient_table.to_csv(coefficients_path, index=False)
        self._write_json({"observations": analyzer.key_insights()}, insights_path)
        self._write_json(quality_report or {}, quality_path)

        store = SQLiteStore(database_path)
        store.save_leads(data)
        store.source_performance().to_csv(self.output_dir / "sql_source_performance.csv", index=False)

        DashboardCharts.conversion_by_source(source_metrics, self.output_dir / "conversion_by_source.png")
        DashboardCharts.funnel_by_stage(funnel, self.output_dir / "sales_funnel.png")
        DashboardCharts.response_time_by_source(source_metrics, self.output_dir / "response_time_by_source.png")
        joblib.dump(model.pipeline, model_path)

        return {
            "summary": summary_path,
            "source_metrics": source_path,
            "funnel": funnel_path,
            "region_metrics": region_path,
            "lead_scores": scored_path,
            "model_evaluation": model_metrics_path,
            "database": database_path,
            "model": model_path,
            "model_coefficients": coefficients_path,
            "key_insights": insights_path,
            "data_quality": quality_path,
        }
