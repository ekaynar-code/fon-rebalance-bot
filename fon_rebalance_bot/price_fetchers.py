"""
Çoklu varlık türü için fiyat çekme modülü.

Desteklenen türler:
    fund    -> TEFAS (pytefas)
    stock   -> BIST hissesi (Yahoo Finance, .IS son eki otomatik eklenir)
    gold    -> Gram altın (ons altın USD fiyatı x USD/TRY kuru / 31.1035)
    fx      -> Döviz (USD, EUR gibi -> TRY karşılığı, Yahoo Finance)
    crypto  -> Kripto (Binance public API, doğrudan *TRY paritesi)
    cash    -> Sabit değer (vadeli mevduat, nakit) - piyasa fiyatı yok, 1.0 döner
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import requests

try:
    import yfinance as yf
except ImportError:  # pragma: no cover
    yf = None

from tefas_client import get_latest_price as get_fund_price

GRAM_PER_OUNCE = 31.1034768


@dataclass
class PriceResult:
    price_try: float
    as_of: str


class PriceFetchError(RuntimeError):
    pass


def _require_yfinance():
    if yf is None:
        raise PriceFetchError(
            "yfinance kurulu değil. 'pip install yfinance' ile kur."
        )


def get_stock_price(code: str) -> PriceResult:
    """BIST hissesi - code örn. 'THYAO', 'ASELS'. Otomatik '.IS' eklenir."""
    _require_yfinance()
    ticker = code if code.endswith(".IS") else f"{code}.IS"
    try:
        hist = yf.Ticker(ticker).history(period="5d")
        if hist.empty:
            raise PriceFetchError(f"'{code}' için hisse verisi bulunamadı.")
        last_close = float(hist["Close"].iloc[-1])
        last_date = str(hist.index[-1].date())
        return PriceResult(price_try=last_close, as_of=last_date)
    except PriceFetchError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise PriceFetchError(f"'{code}' hisse fiyatı çekilemedi: {exc}") from exc


def get_usdtry() -> float:
    _require_yfinance()
    hist = yf.Ticker("USDTRY=X").history(period="5d")
    if hist.empty:
        raise PriceFetchError("USD/TRY kuru çekilemedi.")
    return float(hist["Close"].iloc[-1])


def get_gold_price_gram_try() -> PriceResult:
    """Gram altın (TRY) = ons altın (USD) / 31.1034768 * USD/TRY."""
    _require_yfinance()
    try:
        gold_hist = yf.Ticker("GC=F").history(period="5d")
        if gold_hist.empty:
            raise PriceFetchError("Ons altın verisi bulunamadı.")
        ounce_usd = float(gold_hist["Close"].iloc[-1])
        usdtry = get_usdtry()
        gram_try = (ounce_usd / GRAM_PER_OUNCE) * usdtry
        last_date = str(gold_hist.index[-1].date())
        return PriceResult(price_try=gram_try, as_of=last_date)
    except PriceFetchError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise PriceFetchError(f"Altın fiyatı çekilemedi: {exc}") from exc


def get_fx_price(code: str) -> PriceResult:
    """Döviz - code örn. 'USD', 'EUR'. TRY karşılığını döner."""
    _require_yfinance()
    if code.upper() == "TRY":
        return PriceResult(price_try=1.0, as_of=dt.date.today().isoformat())
    ticker = f"{code.upper()}TRY=X"
    try:
        hist = yf.Ticker(ticker).history(period="5d")
        if hist.empty:
            raise PriceFetchError(f"'{code}' için kur verisi bulunamadı.")
        last_close = float(hist["Close"].iloc[-1])
        last_date = str(hist.index[-1].date())
        return PriceResult(price_try=last_close, as_of=last_date)
    except PriceFetchError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise PriceFetchError(f"'{code}' kuru çekilemedi: {exc}") from exc


def get_crypto_price_try(code: str) -> PriceResult:
    """Kripto - code örn. 'BTC', 'ETH'. Binance'in *TRY paritesini kullanır."""
    symbol = f"{code.upper()}TRY"
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            raise PriceFetchError(
                f"'{code}' için Binance'ten fiyat alınamadı ({resp.status_code}). "
                f"Bu paritenin Binance'te TRY karşılığı olmayabilir."
            )
        data = resp.json()
        price = float(data["price"])
        return PriceResult(price_try=price, as_of=dt.date.today().isoformat())
    except PriceFetchError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise PriceFetchError(f"'{code}' kripto fiyatı çekilemedi: {exc}") from exc


def get_cash_price() -> PriceResult:
    """Sabit değerli varlıklar (vadeli mevduat, nakit) - fiyat her zaman 1.0,
    'units' alanına doğrudan TL tutarını yazman yeterli."""
    return PriceResult(price_try=1.0, as_of=dt.date.today().isoformat())


def get_price(
    instrument_type: str,
    code: str,
    tefas_default_kind: str = "AUTO",
    tefas_kind_overrides: dict | None = None,
) -> PriceResult:
    instrument_type = instrument_type.lower()

    if instrument_type == "fund":
        fp = get_fund_price(
            code,
            default_kind=tefas_default_kind,
            kind_overrides=tefas_kind_overrides or {},
        )
        return PriceResult(price_try=fp.price, as_of=fp.date)

    if instrument_type == "stock":
        return get_stock_price(code)

    if instrument_type == "gold":
        return get_gold_price_gram_try()

    if instrument_type == "fx":
        return get_fx_price(code)

    if instrument_type == "crypto":
        return get_crypto_price_try(code)

    if instrument_type == "cash":
        return get_cash_price()

    raise PriceFetchError(f"Bilinmeyen araç türü: '{instrument_type}'")
