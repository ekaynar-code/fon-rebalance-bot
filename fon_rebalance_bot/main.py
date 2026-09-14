"""
Portföy Rebalancing Sinyal Botu - Ana script (çoklu araç türü destekli).

Çalıştırma:
    python main.py

Ortam değişkenleri (.env dosyasından veya GitHub Secrets'tan gelir):
    GMAIL_ADDRESS
    GMAIL_APP_PASSWORD
    EMAIL_TO   (virgülle ayrılmış birden fazla adres olabilir)
"""
from __future__ import annotations

import os
import sys
import datetime as dt

import yaml
from dotenv import load_dotenv

from price_fetchers import get_price, PriceFetchError
from rebalance import evaluate_portfolio
from email_notify import send_email, EmailNotifyError


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_message(statuses, total_value: float) -> str:
    today = dt.date.today().isoformat()
    lines = [f"Portföy Durumu - {today}", ""]

    any_signal = any(s.needs_rebalance for s in statuses)

    for s in statuses:
        flag = "[SİNYAL VAR]" if s.needs_rebalance else "[OK]"
        lines.append(
            f"{flag} {s.code} - {s.name}\n"
            f"   Güncel: %{s.current_weight*100:.1f}  |  Hedef: %{s.target_weight*100:.1f}"
            f"  |  Sapma: {s.deviation_pct_points:+.1f} puan"
        )
        if s.needs_rebalance:
            lines.append(
                f"   Öneri: {s.suggested_action} ~ {s.suggested_amount_try:,.0f} TL"
            )
        lines.append("")
