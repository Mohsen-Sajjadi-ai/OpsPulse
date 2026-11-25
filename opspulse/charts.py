"""Matplotlib visualizations for the generated operations report."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


class DashboardCharts:
    @staticmethod
    def conversion_by_source(source_metrics: pd.DataFrame, output_path: str | Path) -> None:
        data = source_metrics.sort_values("conversion_rate", ascending=False)
        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.bar(data["lead_source"], data["conversion_rate"] * 100)
        ax.set_title("Lead Conversion Rate by Source")
        ax.set_xlabel("Lead Source")
        ax.set_ylabel("Conversion Rate (%)")
        ax.set_ylim(0, max(10, float(data["conversion_rate"].max() * 120)))
        ax.tick_params(axis="x", rotation=20)
        ax.grid(axis="y", alpha=0.25)
        for bar, value in zip(bars, data["conversion_rate"] * 100):
            ax.annotate(f"{value:.1f}%", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 4), textcoords="offset points", ha="center", fontsize=8)
        fig.tight_layout()
        fig.savefig(output_path, dpi=160)
        plt.close(fig)

    @staticmethod
    def funnel_by_stage(funnel: pd.DataFrame, output_path: str | Path) -> None:
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(funnel["sales_stage"], funnel["leads"])
        ax.set_title("CRM Pipeline Stage Distribution")
        ax.set_xlabel("Sales Stage")
        ax.set_ylabel("Number of Leads")
        ax.tick_params(axis="x", rotation=20)
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        fig.savefig(output_path, dpi=160)
        plt.close(fig)

    @staticmethod
    def response_time_by_source(source_metrics: pd.DataFrame, output_path: str | Path) -> None:
        data = source_metrics.sort_values("avg_response_hours", ascending=True)
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.barh(data["lead_source"], data["avg_response_hours"])
        ax.set_title("Average First Response Time by Lead Source")
        ax.set_xlabel("Average Response Time (hours)")
        ax.set_ylabel("Lead Source")
        ax.grid(axis="x", alpha=0.25)
        fig.tight_layout()
        fig.savefig(output_path, dpi=160)
        plt.close(fig)
