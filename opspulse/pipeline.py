"""Top-level OpsPulse application workflow."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .data import CRMDataLoader
from .model import LeadConversionModel
from .reporting import ReportBuilder


class OpsPulsePipeline:
    def __init__(self, input_path: str | Path, output_dir: str | Path) -> None:
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir)
        self.loader = CRMDataLoader()

    def run(self) -> dict[str, Any]:
        data = self.loader.load(self.input_path)
        quality = self.loader.quality_report(data)
        model = LeadConversionModel(random_state=42)
        evaluation = model.evaluate(data)
        # Refit on the full synthetic dataset only after held-out evaluation for scoring.
        model.fit(data)
        quality_dict = {
            "rows": quality.row_count,
            "columns": quality.column_count,
            "duplicate_lead_ids": quality.duplicate_lead_ids,
            "missing_cells": quality.missing_cells,
            "conversion_rate": quality.conversion_rate,
        }
        output_paths = ReportBuilder(self.output_dir).build(
            data, model, evaluation.to_dict(), quality_dict
        )
        return {
            "quality": {
                "rows": quality.row_count,
                "columns": quality.column_count,
                "duplicate_ids": quality.duplicate_lead_ids,
                "missing_cells": quality.missing_cells,
                "conversion_rate": quality.conversion_rate,
            },
            "model_evaluation": evaluation.to_dict(),
            "output_paths": output_paths,
        }
