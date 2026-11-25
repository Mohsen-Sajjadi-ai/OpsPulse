# OpsPulse technical interview guide

## 60-second overview

"I built OpsPulse as a small end-to-end information-systems project. It validates CRM data,
calculates operating and sales KPIs, persists the records in SQLite, and produces charts
and reports. I also added a logistic-regression baseline to demonstrate a transparent
machine-learning workflow. The project uses synthetic records, so I describe the results as
a technical demonstration rather than production evidence."

## Likely questions and answer points

### Why did you use object-oriented design?

The main responsibilities are separated into classes: loading and validation, operational
analysis, model training, persistence, charting, report generation, and orchestration. This
makes the modules easier to test, replace, and extend than one long script.

### What does the data-validation layer check?

It checks the required schema, empty data, unique lead IDs, missing or blank categories,
valid dates, numeric types, non-negative counts/times/values, and a binary conversion target.

### Why use pandas and NumPy?

Pandas handles tabular ingestion, cleaning, grouping, aggregation, and CSV reporting. NumPy
supports numerical operations, probability calculations in the sample-data generator, and
model output handling.

### Why logistic regression?

It is a relatively interpretable classification baseline. It produces probabilities and
coefficients that can be discussed, and it is appropriate for demonstrating a first model
before trying more complex approaches.

### How did you evaluate the model?

I used a stratified hold-out test split, then reported accuracy, precision, recall, F1, ROC-AUC,
and the confusion matrix. The fixed seed makes the demonstration repeatable.

### What is target leakage, and how did you reduce it?

Target leakage happens when model inputs contain information that would not legitimately be
available at prediction time or directly reveals the outcome. I excluded `sales_stage` and
`deal_value_usd` from the feature set because those fields can be outcome-adjacent.

### Why are the metrics modest?

The dataset is synthetic and deliberately includes randomness. The point is to demonstrate
correct workflow and honest evaluation, not to optimize a model against artificial labels.
A production model would need representative historical data and a carefully defined target.

### What would you improve next?

I would add a time-based validation split, probability calibration, group-level error
analysis, stronger data lineage, logging, monitoring, role-based database access, and a
controlled API integration. I would also compare a simple baseline with tree-based models.

### How would you add a Generative AI component responsibly?

I would send only approved, aggregated, non-sensitive KPI summaries to an LLM, request a
strict structured output, validate the response against a schema, and keep the generated
narrative separate from the underlying measured metrics. I would not let a language model
silently change source data or make customer decisions.
