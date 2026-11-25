# Portfolio and resume notes

## Resume bullet (use after you have run the project and can explain it)

Built **OpsPulse**, an object-oriented Python analytics pipeline that validates CRM records,
calculates sales and operational KPIs, stores data in SQLite, and generates Matplotlib
reports. Implemented a scikit-learn logistic-regression baseline with a leakage-aware
feature set and hold-out evaluation; documented the workflow and added automated tests.

## Short portfolio description

OpsPulse is a reproducible business-operations analytics project demonstrating Python,
pandas, NumPy, scikit-learn, SQL/SQLite, Matplotlib, object-oriented design, data validation,
and baseline machine-learning evaluation over a clearly labeled synthetic CRM dataset.

## Be ready to explain

- Why a train/test split is needed.
- What precision and recall mean in a lead-prioritization context.
- Why `sales_stage` is excluded from the model's feature inputs.
- Why synthetic-data metrics do not prove real-world model performance.
- How you would secure and govern access to a real CRM dataset.
- What monitoring you would add before a production deployment.

## 60-second project explanation

"I built OpsPulse to demonstrate an end-to-end business information workflow. It starts by
validating a CRM export, then calculates operational KPIs such as conversion rate, first
response time, and pipeline value. I used an object-oriented design to separate data
validation, analysis, modeling, storage, and reporting. For the predictive component, I
trained a logistic-regression baseline and evaluated it on a stratified hold-out set. I
excluded the sales stage and deal value from model inputs to avoid leakage. The results are
clearly labeled as a synthetic-data demonstration, so I do not claim that the metrics
represent production performance."
