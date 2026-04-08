__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'

from clients import CoinMarketCapClient


def test_rsi_overall() -> None:
    with CoinMarketCapClient() as client:
        overall = client.fetch_overral_rsi()
        assert overall is not None
        assert overall.oversold_count > 0
        assert overall.overbought_count > 0


def test_rsi_item() -> None:
    with CoinMarketCapClient() as client:
        data = client.fetch_rsi()
        assert len(data) > 0
        for item in data:
            assert item.rsi15m is not None
            assert item.rsi1h is not None
            assert item.rsi4h is not None
            assert item.rsi24h is not None
            assert item.rsi7d is not None
