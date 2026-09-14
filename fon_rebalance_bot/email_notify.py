"""
Gmail SMTP üzerinden e-posta bildirimi gönderir.

Kurulum:
1. Google Hesabında 2 Adımlı Doğrulama'yı aç (zaten açık değilse):
   https://myaccount.google.com/security
2. "Uygulama Şifreleri" oluştur:
   https://myaccount.google.com/apppasswords
   Uygulama olarak "Diğer" seç, bir isim ver (örn. "Fon Botu"), oluştur.
3. Sana 16 haneli bir şifre verecek (boşluksuz kullan) — bu GMAIL_APP_PASSWORD'dür.
   NOT: Bu senin normal Gmail şifren DEĞİL, ayrı bir uygulama şifresidir.
"""
from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


class EmailNotifyError(RuntimeError):
    pass


def send_email(
    gmail_address: str,
    gmail_app_password: str,
    to_addresses: list[str],
    subject: str,
    body: str,
) -> None:
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = ", ".join(to_addresses)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(gmail_address, gmail_app_password)
            server.sendmail(gmail_address, to_addresses, msg.as_string())
    except Exception as exc:  # noqa: BLE001
        raise EmailNotifyError(f"E-posta gönderilemedi: {exc}") from exc
