"""Command-line entry point for OpsPulse."""
from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import OpsPulsePipeline


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Run the OpsPulse CRM analytics pipeline.")
    parser.add_argument(
        "--input",
        default=str(project_root / "sample_data" / "crm_leads.csv"),
        help="Path to a CRM CSV file matching the documented schema.",
    )
    parser.add_argument(
        "--output",
        default=str(project_root / "outputs"),
        help="Directory where reports, charts, database, and model are saved.",
    )
    args = parser.parse_args()

    result = OpsPulsePipeline(args.input, args.output).run()
    quality = result["quality"]
    metrics = result["model_evaluation"]
    print("\nOPSPULSE — BUSINESS OPERATIONS INTELLIGENCE")
    print("=" * 48)
    print(f"Rows processed:       {quality['rows']}")
    print(f"Columns validated:    {quality['columns']}")
    print(f"Duplicate lead IDs:   {quality['duplicate_ids']}")
    print(f"Missing cells:        {quality['missing_cells']}")
    print(f"Observed conversion:  {quality['conversion_rate']:.1%}")
    print("\nHELD-OUT MODEL EVALUATION (synthetic data)")
    print(f"Accuracy:             {metrics['accuracy']:.3f}")
    print(f"Precision:            {metrics['precision']:.3f}")
    print(f"Recall:               {metrics['recall']:.3f}")
    print(f"F1:                   {metrics['f1']:.3f}")
    print(f"ROC-AUC:              {metrics['roc_auc']:.3f}")
    print(f"\nReports saved to: {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
