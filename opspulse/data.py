"""CRM data loading and validation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


class DataValidationError(ValueError):
    """Raised when source CRM data does not meet the expected contract."""


REQUIRED_COLUMNS = {
    "lead_id",
    "created_at",
    "region",
    "industry",
    "company_size",
    "lead_source",
    "response_time_hours",
    "interactions_count",
    "previous_purchases",
    "sales_stage",
    "deal_value_usd",
    "converted",
}

NUMERIC_COLUMNS = (
    "response_time_hours",
    "interactions_count",
    "previous_purchases",
    "deal_value_usd",
    "converted",
)


@dataclass(frozen=True)
class DataQualityReport:
    row_count: int
    column_count: int
    duplicate_lead_ids: int
    missing_cells: int
    conversion_rate: float


class CRMDataLoader:
    """Load and validate a CRM export against OpsPulse's documented schema."""

    def __init__(self, required_columns: Iterable[str] = REQUIRED_COLUMNS) -> None:
        self.required_columns = set(required_columns)

    def load(self, file_path: str | Path) -> pd.DataFrame:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        data = pd.read_csv(path)
        self.validate(data)

        clean = data.copy()
        clean["created_at"] = pd.to_datetime(clean["created_at"], errors="coerce")
        if clean["created_at"].isna().any():
            raise DataValidationError("'created_at' contains missing or invalid dates.")

        for column in NUMERIC_COLUMNS:
            clean[column] = pd.to_numeric(clean[column], errors="coerce")
            if clean[column].isna().any():
                raise DataValidationError(f"'{column}' contains non-numeric or missing values.")

        clean["lead_id"] = clean["lead_id"].astype(str).str.strip()
        for column in ("region", "industry", "company_size", "lead_source", "sales_stage"):
            clean[column] = clean[column].astype(str).str.strip()

        self._validate_ranges(clean)
        return clean

    def validate(self, data: pd.DataFrame) -> None:
        missing = self.required_columns.difference(data.columns)
        if missing:
            raise DataValidationError(
                "Missing required columns: " + ", ".join(sorted(missing))
            )
        if data.empty:
            raise DataValidationError("The CRM dataset is empty.")
        if data["lead_id"].isna().any():
            raise DataValidationError("'lead_id' cannot contain missing values.")
        if data["lead_id"].astype(str).str.strip().eq("").any():
            raise DataValidationError("'lead_id' cannot contain blank values.")
        if data["lead_id"].astype(str).str.strip().duplicated().any():
            raise DataValidationError("'lead_id' must be unique; duplicate IDs found.")

        categorical = ("region", "industry", "company_size", "lead_source", "sales_stage")
        for column in categorical:
            if data[column].isna().any() or data[column].astype(str).str.strip().eq("").any():
                raise DataValidationError(f"'{column}' cannot contain missing or blank values.")

    @staticmethod
    def _validate_ranges(data: pd.DataFrame) -> None:
        if (data["response_time_hours"] < 0).any():
            raise DataValidationError("'response_time_hours' cannot be negative.")
        if (data["interactions_count"] < 0).any():
            raise DataValidationError("'interactions_count' cannot be negative.")
        if (data["previous_purchases"] < 0).any():
            raise DataValidationError("'previous_purchases' cannot be negative.")
        if (data["deal_value_usd"] < 0).any():
            raise DataValidationError("'deal_value_usd' cannot be negative.")
        if not data["converted"].isin([0, 1]).all():
            raise DataValidationError("'converted' must contain only 0 or 1.")

    @staticmethod
    def quality_report(data: pd.DataFrame) -> DataQualityReport:
        return DataQualityReport(
            row_count=int(len(data)),
            column_count=int(data.shape[1]),
            duplicate_lead_ids=int(data["lead_id"].duplicated().sum()),
            missing_cells=int(data.isna().sum().sum()),
            conversion_rate=float(data["converted"].mean()),
        )
