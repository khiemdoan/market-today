import os
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from telegram import Telegram

FIG_SIZE = (20, 15)
TOP_N = 10


def _get_top10_banks(df: pd.DataFrame, term: str) -> list[str]:
    latest = df.dropna(subset=[term]).sort_values('date', ascending=False).drop_duplicates('bank')
    return latest.nlargest(TOP_N, term)['bank'].tolist()


def plot_top10_interest_rates(csv_path: str, term: str = '12_months') -> bytes:
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])

    top10_banks = _get_top10_banks(df, term)
    top10_df = df[df['bank'].isin(top10_banks)]

    fig, ax = plt.subplots(1)

    g = sns.lineplot(data=top10_df, x='date', y=term, hue='bank', hue_order=top10_banks, ax=ax)
    sns.move_legend(g, 'center left', bbox_to_anchor=(1, 0.5))
    g.set_ylabel('Interest rate (%)')
    g.tick_params(axis='y', labelsize=10)
    g.tick_params(axis='x', labelrotation=30, labelsize=10)

    fig.tight_layout()
    fig.suptitle(f'Vietnam interest rate ({term})')
    fig.subplots_adjust(top=0.92)

    with BytesIO() as img:
        fig.savefig(img, format='jpg')
        img.seek(0)
        return img.read()


def _get_csv_path() -> Path:
    return Path(__file__).resolve().parent.parent / 'data' / 'interest_rates.csv'


def send_plot_to_telegram(term: str = '12_months') -> None:
    csv_path = _get_csv_path()
    if not csv_path.exists():
        raise FileNotFoundError(f'CSV not found: {csv_path}')

    img_bytes = plot_top10_interest_rates(str(csv_path), term=term)
    caption = f'Top 10 banks - interest rate ({term}) over time'

    with Telegram() as tele:
        tele.send_photo(img_bytes, caption=caption)
    print('Plot sent to Telegram')


def test_plot_top10_interest_rates() -> None:
    csv_path = _get_csv_path()
    img_bytes = plot_top10_interest_rates(str(csv_path), term='12_months')
    assert isinstance(img_bytes, bytes)
    Path('test_top10_interest_rates.jpg').write_bytes(img_bytes)
    print('Test passed: Image saved as test_top10_interest_rates.jpg')


if __name__ == '__main__':
    if os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'):
        send_plot_to_telegram(term='12_months')
    else:
        test_plot_top10_interest_rates()
