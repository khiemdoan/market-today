from clients import YahooClient
from graph import draw_klines
from telegram import Telegram
from templates import Render


def main() -> None:
    with YahooClient() as client:
        df = client.get_gold()

    if df.shape[0] < 2:
        raise RuntimeError("Not enough data to send signal")

    date = df.iloc[-1]["open_time"]
    value = df.iloc[-1]["close"]
    prev = df.iloc[-2]["close"]
    delta = value - prev

    caption = Render()(
        "gold.j2",
        context={
            "date": date,
            "value": value,
            "delta": delta,
        },
    )

    img = draw_klines(df)

    with Telegram() as tele:
        tele.send_photo(img, caption=caption)


if __name__ == '__main__':
    main()
