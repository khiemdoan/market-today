import os
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from telegram import Telegram

ROWS, COLS = 5, 2
FIG_SIZE = (30, 15)
TOP_N = 10


def _get_top10_banks(df: pd.DataFrame, term: str) -> list[str]:
    latest = (
        df.dropna(subset=[term])
        .sort_values("date", ascending=False)
        .drop_duplicates("bank")
    )
    return latest.nlargest(TOP_N, term)["bank"].tolist()


def _format_rate_change(current: float, prev: float | None) -> str:
    if prev is None:
        return "-"
    delta = current - prev
    return f"{delta:+.2f}pp" if delta != 0 else "0pp"


def _draw_bank_chart(ax, bank_df: pd.DataFrame, bank: str, term: str) -> None:
    sns.lineplot(bank_df, x="date", y=term, ax=ax)

    current_rate = bank_df[term].iloc[-1]
    prev_rate = bank_df[term].iloc[-2] if len(bank_df) >= 2 else None
    delta_str = _format_rate_change(current_rate, prev_rate)

    ax.set_title(f"{bank} | {term}: {current_rate}% ({delta_str})", fontsize=15)
    ax.set_ylabel("Interest rate (%)")
    ax.tick_params(axis="y", labelsize=10)
    ax.tick_params(axis="x", labelrotation=30, labelsize=10)


def plot_top10_interest_rates(csv_path: str, term: str = "12_months") -> bytes:

    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])

    top10_banks = _get_top10_banks(df, term)
    df_top10 = df[df["bank"].isin(top10_banks)]

    fig, axes = plt.subplots(ROWS, COLS, figsize=FIG_SIZE, sharex=True)
    axes_flat = axes.flatten()

    for idx, bank in enumerate(top10_banks):
        bank_df = (
            df_top10[df_top10["bank"] == bank]
            .dropna(subset=[term])
            .sort_values("date")
        )
        _draw_bank_chart(axes_flat[idx], bank_df, bank, term)

    fig.tight_layout()
    fig.suptitle(f"Top 10 banks with highest interest rate ({term})", fontsize=20)
    fig.subplots_adjust(top=0.92)

    with BytesIO() as img:
        fig.savefig(img, format="jpg")
        img.seek(0)
        return img.read()


def _get_csv_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "interest_rates.csv"


def send_plot_to_telegram(term: str = "12_months") -> None:
    csv_path = _get_csv_path()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    img_bytes = plot_top10_interest_rates(str(csv_path), term=term)
    caption = f"Top 10 banks - interest rate ({term}) over time"

    with Telegram() as tele:
        tele.send_photo(img_bytes, caption=caption)
    print("Plot sent to Telegram")

def test_plot_top10_interest_rates() -> None:
    csv_path = _get_csv_path()
    img_bytes = plot_top10_interest_rates(str(csv_path), term="12_months")
    assert isinstance(img_bytes, bytes)
    Path("test_top10_interest_rates.jpg").write_bytes(img_bytes)
    print("Test passed: Image saved as test_top10_interest_rates.jpg")


if __name__ == "__main__":
    if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        send_plot_to_telegram(term="12_months")
    else:
        test_plot_top10_interest_rates()
