# Fon Rebalancing Sinyal Botu

TEFAS'taki fonlarının hedef ağırlıklardan ne kadar saptığını her gün otomatik
kontrol edip Telegram'a bildirim gönderen bot. **Emri kendin girersin** — bot
hiçbir aracı kurumda otomatik alım/satım yapmaz, sadece "şunu al / şunu sat"
sinyali üretir.

## 1. Telegram Bot Oluşturma

1. Telegram'da **@BotFather**'ı bul, `/newbot` yaz, adım adım ilerle.
2. Sana bir **token** verecek (örn. `123456789:AAExample...`), sakla.
3. Yeni botuna Telegram'dan bir mesaj at (örn. "merhaba") — bot seninle
   konuşmamışsa mesaj gönderemez.
4. Tarayıcından şu adrese git (TOKEN'ı kendi tokenınla değiştir):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
5. Dönen JSON içinde `"chat":{"id": 123456789, ...}` kısmındaki `id`
   değerini **CHAT_ID** olarak not al.

## 2. config.yaml'ı Düzenle

`config.yaml` dosyasını aç ve:
- `funds` altına kendi fonlarının **TEFAS kodlarını** (örn. AAK, TCD),
  **hedef ağırlıklarını** (toplamları 1.0 etmeli) ve **elinde bulunan pay
  adedini** (`units`) gir.
- Her fon alım/satımından sonra `units` alanını elle güncellemen gerekir
  (bot senin hesabına erişemediği için bunu otomatik bilemez).
- `rebalance` altında eşikleri istersen değiştir (varsayılan: 5/25 kuralı).

## 3. Yerel Test (opsiyonel ama önerilir)

```bash
cd fon_rebalance_bot
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını aç, TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID'yi gir
python main.py
```

Telegram'a mesaj geldiyse her şey doğru çalışıyor demektir.

## 4. GitHub'a Yükleyip Otomatikleştirme

1. Bu klasörü kendi **private** bir GitHub reposuna yükle (fon bilgilerin
   ve stratejin görünmesin diye private öneriyoruz).
2. Repo → **Settings → Secrets and variables → Actions → New repository
   secret** ile şu iki secret'ı ekle:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. `.github/workflows/rebalance.yml` zaten hazır — her hafta içi günü
   20:00 (TR saati) otomatik çalışacak şekilde ayarlı.
4. İstersen repo → **Actions** sekmesinden **"Run workflow"** ile manuel de
   tetikleyebilirsin.

## 5. Sorun Giderme

- **"için fiyat bulunamadı" hatası:** Fon kodunu kontrol et (TEFAS'ta fon
  arama sayfasından doğrula). `tefas.kind_overrides` içine örn.
  `{"AAK": "YAT"}` ekleyerek fon türünü sabitlemeyi dene.
- **`pytefas` çalışmıyor / hata veriyor:** TEFAS sitesi zaman zaman API'sini
  değiştirebiliyor. Önce `pip install --upgrade pytefas` dene. Sorun
  sürerse GitHub'da `pytefas` reposunun (mirzazad/pytefas) issue/README
  kısmına bak, gerekirse alternatif olarak `tefasmak` paketine geçilebilir.
- **Telegram mesajı gelmiyor:** Bot ile önce sen konuşmuş musun kontrol et
  (BotFather'dan yeni açılan botlar, kullanıcı ilk mesajı atmadan mesaj
  gönderemez). CHAT_ID'yi tekrar `getUpdates` ile doğrula.
- **GitHub Actions çalışmıyor:** Actions sekmesinde workflow'un loglarına
  bak; genelde secret isimlerinin `config.yaml`'daki değil `Settings →
  Secrets` içindeki isimlerle birebir aynı olması gerekir.

## Önemli Notlar

- Bu bot **yatırım tavsiyesi değildir**, sadece senin belirlediğin hedef
  ağırlıklara göre matematiksel bir sapma hesabı yapar.
- TEFAS fiyatları genelde akşam saatlerinde (~19:00-20:30 TR) netleşir; bot
  bu yüzden 20:00'de çalışacak şekilde ayarlandı. Daha erken çalıştırırsan
  önceki günün fiyatını görebilirsin.
- `units` alanını güncel tutmazsan hesaplamalar yanlış çıkar — bu en sık
  yapılan hata.
