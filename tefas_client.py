"""
TEFAS fiyat verisi çekme modülü.

TEFAS sitesi 2026'da Next.js altyapısına geçti; eski BindHistoryInfo endpoint'i
kapandı. Bu modül yeni endpoint'leri kullanan `pytefas` paketine sarmalayıcıdır.

pytefas çalışmazsa (paket güncellenmemiş / TEFAS tekrar değiştirmiş olabilir):
    pip install --upgrade pytefas
komutunu dene. Yine de sorun sürerse README'deki "Sorun Giderme" bölümüne bak.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from pytefas import Crawler

FUND_KINDS = ["YAT", "EMK", "BYF", "GYF", "GSYF"]


@dataclass
class FundPrice:
    code: str
    price: float
    date: str


class TefasClientError(RuntimeError):
    pass


def get_latest_price(fund_code: str, default_kind: str = "AUTO",
                      kind_overrides: dict | None = None,
                      lookback_days: int = 10) -> FundPrice:
    """
    Belirtilen fon kodu için son bilinen fiyatı döndürür.

    Hafta sonu / resmi tatil gibi günlerde TEFAS veri açıklamadığından,
    son `lookback_days` gün içindeki en güncel veriyi arar.
    """
    kind_overrides = kind_overrides or {}
    forced_kind = kind_overrides.get(fund_code)
    kinds_to_try = [forced_kind] if forced_kind else (
        FUND_KINDS if default_kind == "AUTO" else [default_kind]
    )

    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=lookback_days)

    crawler = Crawler()
    last_error = None

    for kind in kinds_to_try:
        try:
            df = crawler.fetch(
                start_date.isoformat(),
                end_date.isoformat(),
                kind=kind,
                fund_code=fund_code,
            )
        except Exception as exc:  # noqa: BLE001 - dış servis hatalarını topluyoruz
            last_error = exc
            continue

        if df is None or len(df) == 0:
            continue

        df_sorted = df.sort_values("date")
        last_row = df_sorted.iloc[-1]
        return FundPrice(
            code=fund_code,
            price=float(last_row["price"]),
            date=str(last_row["date"]),
        )

    raise TefasClientError(
        f"'{fund_code}' için fiyat bulunamadı (denenen türler: {kinds_to_try}). "
        f"Son hata: {last_error}"
    )
