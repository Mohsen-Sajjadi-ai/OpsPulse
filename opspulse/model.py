
"""Leakage-aware baseline model for lead conversion propensity."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_predict,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


CATEGORICAL_FEATURES = [
    "region",
    "industry",
    "company_size",
    "lead_source",
]

NUMERIC_FEATURES = [
    "response_time_hours",
    "interactions_count",
    "previous_purchases",
]

FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES
TARGET = "converted"


@dataclass
class ModelEvaluation:
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    train_rows: int
    test_rows: int
    confusion_matrix: list[list[int]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "roc_auc": self.roc_auc,
            "train_rows": self.train_rows,
            "test_rows": self.test_rows,
            "confusion_matrix": self.confusion_matrix,
        }


class LeadConversionModel:
    """An interpretable logistic-regression baseline."""

    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state
        self.pipeline: Pipeline | None = None

    @staticmethod
    def _build_pipeline() -> Pipeline:
        preprocess = ColumnTransformer(
            transformers=[
                (
                    "categorical",
                    OneHotEncoder(handle_unknown="ignore"),
                    CATEGORICAL_FEATURES,
                ),
                (
                    "numeric",
                    StandardScaler(),
                    NUMERIC_FEATURES,
                ),
            ]
        )

        return Pipeline(
            steps=[
                ("preprocess", preprocess),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                    ),
                ),
            ]
        )

    def evaluate(
        self,
        data: pd.DataFrame,
        test_size: float = 0.25,
    ) -> ModelEvaluation:

        if data[TARGET].nunique() < 2:
            raise ValueError(
                "Model evaluation requires both converted and non-converted leads."
            )

        X = data[FEATURES]
        y = data[TARGET].astype(int)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=self.random_state,
            stratify=y,
        )

        evaluator = self._build_pipeline()
        evaluator.fit(X_train, y_train)

        predictions = evaluator.predict(X_test)
        probabilities = evaluator.predict_proba(X_test)[:, 1]

        evaluation = ModelEvaluation(
            accuracy=float(accuracy_score(y_test, predictions)),
            precision=float(
                precision_score(y_test, predictions, zero_division=0)
            ),
            recall=float(
                recall_score(y_test, predictions, zero_division=0)
            ),
            f1=float(
                f1_score(y_test, predictions, zero_division=0)
            ),
            roc_auc=float(
                roc_auc_score(y_test, probabilities)
            ),
            train_rows=int(len(X_train)),
            test_rows=int(len(X_test)),
            confusion_matrix=confusion_matrix(
                y_test,
                predictions,
                labels=[0, 1],
            ).tolist(),
        )

        self.pipeline = evaluator
        return evaluation

    def fit(self, data: pd.DataFrame) -> "LeadConversionModel":
        self.pipeline = self._build_pipeline()

        self.pipeline.fit(
            data[FEATURES],
            data[TARGET].astype(int),
        )

        return self

    def predict_probabilities(
        self,
        data: pd.DataFrame,
    ) -> np.ndarray:

        if self.pipeline is None:
            raise RuntimeError(
                "Model has not been fitted. Call evaluate() or fit() first."
            )

        return self.pipeline.predict_proba(data[FEATURES])[:, 1]

    def coefficient_table(self) -> pd.DataFrame:
        """Return logistic-regression coefficients and odds ratios."""

        if self.pipeline is None:
            raise RuntimeError(
                "Model has not been fitted. Call evaluate() or fit() first."
            )

        preprocessor = self.pipeline.named_steps["preprocess"]
        classifier = self.pipeline.named_steps["classifier"]

        feature_names = preprocessor.get_feature_names_out()
        coefficients = classifier.coef_[0]

        table = pd.DataFrame({
            "feature": feature_names,
            "coefficient": coefficients,
            "odds_ratio": np.exp(
                np.clip(coefficients, -20, 20)
            ),
        })

        return table.reindex(
            table["coefficient"].abs().sort_values(
                ascending=False
            ).index
        ).reset_index(drop=True)

    def score_leads_out_of_fold(
        self,
        data: pd.DataFrame,
        n_splits: int = 5,
    ) -> pd.DataFrame:
        """Score historical leads using out-of-fold predictions."""

        y = data[TARGET].astype(int)

        if y.nunique() < 2:
            raise ValueError(
                "Out-of-fold scoring requires both target classes."
            )

        if n_splits < 2 or int(y.value_counts().min()) < n_splits:
            raise ValueError(
                "Not enough samples in each class for the requested folds."
            )

        cv = StratifiedKFold(
            n_splits=n_splits,
            shuffle=True,
            random_state=self.random_state,
        )

        probabilities = cross_val_predict(
            self._build_pipeline(),
            data[FEATURES],
            y,
            cv=cv,
            method="predict_proba",
        )[:, 1]

        scored = data.copy()
        scored["conversion_probability"] = probabilities

        scored["priority_band"] = pd.cut(
            probabilities,
            bins=[-0.001, 0.35, 0.65, 1.001],
            labels=["Low", "Medium", "High"],
        ).astype(str)

        return scored.sort_values(
            "conversion_probability",
            ascending=False,
        )

    def score_leads(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:

        scored = data.copy()

        scored["conversion_probability"] = (
            self.predict_probabilities(data)
        )

        scored["priority_band"] = pd.cut(
            scored["conversion_probability"],
            bins=[-0.001, 0.35, 0.65, 1.001],
            labels=["Low", "Medium", "High"],
        ).astype(str)

        return scored.sort_values(
            "conversion_probability",
            ascending=False,
        )
