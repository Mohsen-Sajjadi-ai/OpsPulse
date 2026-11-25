# OpsPulse data dictionary

The included CSV is **synthetic demonstration data**. It contains no real customer records.

| Field | Type | Meaning |
|---|---|---|
| `lead_id` | string | Unique synthetic CRM lead identifier |
| `created_at` | date | Lead creation date |
| `region` | category | Broad region |
| `industry` | category | Organization industry |
| `company_size` | category | SMB, Mid-Market, or Enterprise |
| `lead_source` | category | Acquisition channel |
| `response_time_hours` | number | Time to first response in hours |
| `interactions_count` | integer | Recorded engagement count |
| `previous_purchases` | integer | Prior purchases attributed to the account |
| `sales_stage` | category | Current pipeline stage |
| `deal_value_usd` | number | Synthetic opportunity value in USD |
| `converted` | binary | 1 if converted in the synthetic example, else 0 |

## Modeling policy

The baseline model uses `region`, `industry`, `company_size`, `lead_source`,
`response_time_hours`, `interactions_count`, and `previous_purchases`. It excludes
`sales_stage` and `deal_value_usd` to reduce target leakage. The example data is generated
from a synthetic process, so model metrics are demonstrations of the evaluation workflow,
not evidence of real-world predictive performance.
