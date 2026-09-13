"""
Fon Rebalancing Sinyal Botu - Ana script.

Çalıştırma:
    python main.py

Ortam değişkenleri (.env dosyasından veya GitHub Secrets'tan gelir):
    TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID
"""
from __future__ import annotations

import os
import sys
import datetime as dt

import yaml
from dotenv import load_dotenv

from tefas_client import get_latest_price, TefasClientError
from rebalance import evaluate_portfolio
from telegram_notify import send_telegram_message, TelegramNotifyError


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_message(statuses, total_value: float) -> str:
    today = dt.date.today().isoformat()
    lines = [f"*Fon Portföy Durumu* - {today}", ""]

    any_signal = any(s.needs_rebalance for s in statuses)

    for s in statuses:
        flag = "⚠️" if s.needs_rebalance else "✅"
        lines.append(
            f"{flag} `{s.code}` - {s.name}\n"
            f"   Güncel: %{s.current_weight*100:.1f}  |  Hedef: %{s.target_weight*100:.1f}"
            f"  |  Sapma: {s.deviation_pct_points:+.1f} puan"
        )
        if s.needs_rebalance:
            lines.append(
                f"   👉 Öneri: *{s.suggested_action}* ~ {s.suggested_amount_try:,.0f} TL"
            )
        lines.append("")

    lines.append(f"Toplam Portföy Değeri: {total_value:,.0f} TL")

    if not any_signal:
        lines.append("\n_Şu an rebalancing gerekmiyor, tüm fonlar eşik içinde._")

    return "\n".join(lines)


def main() -> int:
    load_dotenv()

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("HATA: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID tanımlı değil.", file=sys.stderr)
        return 1

    config = load_config()
    portfolio_cfg = config["portfolio"]
    rebalance_cfg = config["rebalance"]
    tefas_cfg = config.get("tefas", {})

    default_kind = tefas_cfg.get("default_kind", "AUTO")
    kind_overrides = tefas_cfg.get("kind_overrides", {})

    funds_with_prices = []
    errors = []

    for fund in portfolio_cfg["funds"]:
        code = fund["code"]
        try:
            fp = get_latest_price(
                code,
                default_kind=default_kind,
                kind_overrides=kind_overrides,
            )
            funds_with_prices.append(
                {
                    "code": code,
                    "name": fund.get("name", code),
                    "price": fp.price,
                    "units": float(fund.get("units", 0.0)),
                    "target_weight": float(fund["target_weight"]),
                }
            )
            print(f"[OK] {code}: {fp.price} ({fp.date})")
        except TefasClientError as exc:
            errors.append(str(exc))
            print(f"[HATA] {code}: {exc}", file=sys.stderr)

    if not funds_with_prices:
        error_text = "Hiçbir fon için fiyat çekilemedi:\n" + "\n".join(errors)
        print(error_text, file=sys.stderr)
        try:
            send_telegram_message(bot_token, chat_id, f"🚨 Fon botu hata verdi:\n{error_text}")
        except TelegramNotifyError:
            pass
        return 1

    statuses, total_value = evaluate_portfolio(
        funds_with_prices,
        cash_balance_try=float(portfolio_cfg.get("cash_balance_try", 0.0)),
        cash_target_weight=float(portfolio_cfg.get("cash_target_weight", 0.0)),
        abs_threshold_pct=float(rebalance_cfg["abs_threshold_pct"]),
        rel_threshold_pct=float(rebalance_cfg["rel_threshold_pct"]),
    )

    message = format_message(statuses, total_value)
    print("\n--- Gönderilecek Mesaj ---")
    print(message)

    try:
        send_telegram_message(bot_token, chat_id, message)
    except TelegramNotifyError as exc:
        print(f"HATA: Telegram mesajı gönderilemedi: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
