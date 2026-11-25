"""SQLite persistence and SQL-based source performance query."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


class SQLiteStore:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def save_leads(self, data: pd.DataFrame) -> None:
        with sqlite3.connect(self.database_path) as connection:
            data.to_sql("crm_leads", connection, if_exists="replace", index=False)
            connection.execute("CREATE INDEX IF NOT EXISTS idx_crm_leads_source ON crm_leads(lead_source)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_crm_leads_stage ON crm_leads(sales_stage)")

    def source_performance(self) -> pd.DataFrame:
        query = """
            SELECT
                lead_source,
                COUNT(*) AS leads,
                SUM(converted) AS converted_leads,
                ROUND(AVG(converted), 4) AS conversion_rate,
                ROUND(AVG(response_time_hours), 2) AS avg_response_hours,
                ROUND(SUM(deal_value_usd), 2) AS pipeline_value_usd
            FROM crm_leads
            GROUP BY lead_source
            ORDER BY conversion_rate DESC, leads DESC
        """
        with sqlite3.connect(self.database_path) as connection:
            return pd.read_sql_query(query, connection)
