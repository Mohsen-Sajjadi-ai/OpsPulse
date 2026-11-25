# OpsPulse architecture

```text
Synthetic / approved CRM CSV
           |
           v
   CRMDataLoader + validation
           |
           +------------------------------+
           |                              |
           v                              v
 OperationsAnalyzer              LeadConversionModel
 (KPIs, funnel, sources)          (preprocess + logistic regression)
           |                              |
           +---------------+--------------+
                           |
                           v
                    ReportBuilder
                           |
      +--------------------+----------------------+
      |                    |                      |
      v                    v                      v
 CSV / JSON reports    Matplotlib charts     SQLite database
      |                    |                      |
      +---------- model / KPI interpretation ------+
                           |
                           v
                 Saved model pipeline (joblib)
```

## Design decisions

- **Separation of concerns:** loading/validation, analytics, model training, storage,
  charting, and report generation live in separate modules.
- **OOP:** `CRMDataLoader`, `OperationsAnalyzer`, `LeadConversionModel`, `SQLiteStore`,
  `DashboardCharts`, `ReportBuilder`, and `OpsPulsePipeline` encapsulate responsibilities.
- **Validation first:** required columns, unique identifiers, data types, ranges, and
  missing values are checked before analytics begin.
- **Leakage-aware baseline:** the model excludes post-outcome or highly outcome-adjacent
  fields such as `sales_stage` and `deal_value_usd`.
- **Reproducibility:** fixed random seeds and an explicit hold-out split are used.
- **Transparency:** the data is synthetic and the model is a prioritization aid only.
