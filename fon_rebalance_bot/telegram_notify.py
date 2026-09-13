"""
Telegram Bot API üzerinden mesaj gönderir.

Kurulum:
1. Telegram'da @BotFather ile konuşup /newbot komutuyla bot oluştur, token'ı al.
2. Botuna Telegram'dan bir mesaj at (örn. "merhaba").
3. Tarayıcıdan şu adrese git (TOKEN'ı kendi tokenınla değiştir):
   https://api.telegram.org/bot<TOKEN>/getUpdates
   Dönen JSON içindeki "chat":{"id": ...} değerini CHAT_ID olarak kullan.
"""
from __future__ import annotations

import requests

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramNotifyError(RuntimeError):
    pass


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> None:
    url = TELEGRAM_API_URL.format(token=bot_token)
    resp = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        },
        timeout=15,
    )
    if resp.status_code != 200:
        raise TelegramNotifyError(
            f"Telegram mesajı gönderilemedi ({resp.status_code}): {resp.text}"
        )
