"""Visualization module for Spendable Exploratory Data Analysis (EDA).

Generates focused, high-contrast, publication-quality chart visualizations
saved as PNG images for EDA reports.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless PNG generation
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


class EDAVisualizer:
    """Plotting and visualization engine for EDA reports."""

    def __init__(self, eda_engine: Any, output_dir: str):
        self.eda = eda_engine
        self.df = eda_engine.df
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Custom styling palette
        sns.set_theme(style="whitegrid")
        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.titlesize": 14,
        })

    def generate_all_plots(self) -> List[str]:
        """Generate all required EDA visualizations and return list of filepaths."""
        if self.df.empty:
            return []

        generated_paths = []
        generated_paths.append(self.plot_amount_distribution())
        generated_paths.append(self.plot_monthly_cashflow())
        generated_paths.append(self.plot_user_balance_trajectories())
        generated_paths.append(self.plot_activity_type_distribution())
        generated_paths.append(self.plot_category_distribution())
        generated_paths.append(self.plot_persona_comparison())
        generated_paths.append(self.plot_user_transaction_counts())

        return [str(p) for p in generated_paths if p is not None]

    def plot_amount_distribution(self) -> Path:
        """01: Transaction Amount Distribution (Histogram & Boxplot)."""
        fig, (ax_box, ax_hist) = plt.subplots(
            2, 1, figsize=(10, 6), sharex=True, gridspec_kw={"height_ratios": [0.2, 0.8]}
        )

        amounts = self.df["amount_num"]

        sns.boxplot(x=amounts, ax=ax_box, color="#4C72B0", fliersize=3)
        ax_box.set(xlabel="")
        ax_box.set_title("Spendable Dataset — Transaction Amount Distribution (BDT)", fontsize=13, pad=10)

        sns.histplot(amounts, kde=True, ax=ax_hist, color="#4C72B0", bins=30)
        ax_hist.set_xlabel("Transaction Amount (BDT)")
        ax_hist.set_ylabel("Transaction Count")

        mean_val = amounts.mean()
        median_val = amounts.median()
        ax_hist.axvline(mean_val, color="#C44E52", linestyle="--", linewidth=1.5, label=f"Mean: BDT {mean_val:,.2f}")
        ax_hist.axvline(median_val, color="#55A868", linestyle="-", linewidth=1.5, label=f"Median: BDT {median_val:,.2f}")
        ax_hist.legend(loc="upper right")

        plt.tight_layout()
        filepath = self.output_dir / "01_transaction_amount_distribution.png"
        plt.savefig(filepath, dpi=300)
        plt.close()
        return filepath

    def plot_monthly_cashflow(self) -> Path:
        """02: Monthly Inflow vs Outflow & Net Cash Flow."""
        overview = self.eda.get_dataset_overview()
        monthly_data = overview.get("monthly_summary", [])
        if not monthly_data:
            return None

        m_df = pd.DataFrame(monthly_data)

        fig, ax1 = plt.subplots(figsize=(10, 5))

        x = np.arange(len(m_df))
        width = 0.35

        ax1.bar(x - width/2, m_df["inflow_sum"], width, label="Inflow (BDT)", color="#55A868", alpha=0.85)
        ax1.bar(x + width/2, m_df["outflow_sum"], width, label="Outflow (BDT)", color="#C44E52", alpha=0.85)

        ax1.set_ylabel("Monetary Volume (BDT)")
        ax1.set_title("Monthly Inflow vs Outflow & Net Cash Flow", fontsize=13, pad=10)
        ax1.set_xticks(x)
        ax1.set_xticklabels(m_df["year_month"], rotation=45)

        ax2 = ax1.twinx()
        ax2.plot(x, m_df["net_cashflow"], color="#4C72B0", marker="o", linewidth=2.5, label="Net Cash Flow (BDT)")
        ax2.set_ylabel("Net Cash Flow (BDT)")

        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

        plt.tight_layout()
        filepath = self.output_dir / "02_monthly_inflow_vs_outflow.png"
        plt.savefig(filepath, dpi=300)
        plt.close()
        return filepath

    def plot_user_balance_trajectories(self) -> Path:
        """03: User Balance Progression Trajectories Over Time."""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Select representative users across different account_ids
        users = self.df["account_id"].unique()[:6]
        palette = sns.color_palette("tab10", len(users))

        for idx, uid in enumerate(users):
            u_df = self.df[self.df["account_id"] == uid].sort_values(by="timestamp_dt")
            ax.plot(u_df["timestamp_dt"], u_df["balance_num"], label=uid, color=palette[idx], linewidth=1.8, alpha=0.85)

        ax.set_title("Sample User Account Balance Trajectories Over Simulation Window", fontsize=13, pad=10)
        ax.set_xlabel("Timestamp (UTC)")
        ax.set_ylabel("Account Balance (BDT)")
        ax.axhline(0, color="black", linestyle=":", linewidth=1, alpha=0.7)
        ax.legend(title="User Account", loc="upper right")
        plt.xticks(rotation=30)

        plt.tight_layout()
        filepath = self.output_dir / "03_user_balance_trajectories.png"
        plt.savefig(filepath, dpi=300)
        plt.close()
        return filepath

    def plot_activity_type_distribution(self) -> Path:
        """04: Activity Type Distribution (Count & Monetary Volume)."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        type_counts = self.df["type_clean"].value_counts().reset_index()
        type_counts.columns = ["Activity Type", "Count"]

        type_sums = self.df.groupby("type_clean")["amount_num"].sum().reset_index()
        type_sums.columns = ["Activity Type", "Total Amount"]

        sns.barplot(data=type_counts, x="Count", y="Activity Type", ax=ax1, hue="Activity Type", palette="crest", legend=False)
        ax1.set_title("Transaction Frequency by Activity Type", fontsize=11)
        ax1.set_xlabel("Count")

        sns.barplot(data=type_sums, x="Total Amount", y="Activity Type", ax=ax2, hue="Activity Type", palette="flare", legend=False)
        ax2.set_title("Monetary Volume by Activity Type (BDT)", fontsize=11)
        ax2.set_xlabel("Total Amount (BDT)")
        ax2.set_ylabel("")

        plt.tight_layout()
        filepath = self.output_dir / "04_activity_type_distribution.png"
        plt.savefig(filepath, dpi=300)
        plt.close()
        return filepath

    def plot_category_distribution(self) -> Path:
        """05: Category Distribution (Top Spending Categories)."""
        fig, ax = plt.subplots(figsize=(10, 5))

        cat_sums = self.df.groupby("category")["amount_num"].sum().reset_index()
        cat_sums = cat_sums.sort_values(by="amount_num", ascending=False).head(10)

        sns.barplot(data=cat_sums, x="amount_num", y="category", ax=ax, hue="category", palette="Blues_r", legend=False)
        ax.set_title("Top Domain Spending Categories by Monetary Volume (BDT)", fontsize=13, pad=10)
        ax.set_xlabel("Total Monetary Amount (BDT)")
        ax.set_ylabel("Category")

        plt.tight_layout()
        filepath = self.output_dir / "05_category_distribution.png"
        plt.savefig(filepath, dpi=300)
        plt.close()
        return filepath

    def plot_persona_comparison(self) -> Path:
        """06: Persona Comparison (Net Cash Flow & Balance Volatility)."""
        persona_stats = self.eda.get_persona_sanity_check()
        if not persona_stats:
            return None

        p_df = pd.DataFrame.from_dict(persona_stats, orient="index").reset_index()
        p_df.rename(columns={"index": "Persona"}, inplace=True)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        sns.barplot(data=p_df, x="Persona", y="avg_net_cashflow_per_user", ax=ax1, hue="Persona", palette="Set2", legend=False)
        ax1.set_title("Average Net Cash Flow per User by Persona", fontsize=11)
        ax1.set_ylabel("Net Cash Flow (BDT)")
        ax1.axhline(0, color="black", linestyle="--", linewidth=1)
        ax1.tick_params(axis="x", rotation=30)

        sns.barplot(data=p_df, x="Persona", y="avg_balance_volatility_std", ax=ax2, hue="Persona", palette="Set2", legend=False)
        ax2.set_title("Average Balance Volatility (Std Dev) by Persona", fontsize=11)
        ax2.set_ylabel("Balance Standard Deviation (BDT)")
        ax2.tick_params(axis="x", rotation=30)

        plt.tight_layout()
        filepath = self.output_dir / "06_persona_comparison.png"
        plt.savefig(filepath, dpi=300)
        plt.close()
        return filepath

    def plot_user_transaction_counts(self) -> Path:
        """07: User Transaction Count Distribution."""
        fig, ax = plt.subplots(figsize=(8, 4.5))

        txns_per_user = self.df.groupby("account_id").size()

        sns.histplot(txns_per_user, kde=True, ax=ax, color="#8172B0", discrete=True)
        ax.set_title("Distribution of Transaction Counts per User Account", fontsize=12, pad=10)
        ax.set_xlabel("Total Transactions per User")
        ax.set_ylabel("Number of Users")

        plt.tight_layout()
        filepath = self.output_dir / "07_user_activity_counts.png"
        plt.savefig(filepath, dpi=300)
        plt.close()
        return filepath
