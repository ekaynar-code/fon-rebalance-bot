# Portföy Rebalancing Sinyal Botu

Fon, hisse, altın, döviz, kripto ve nakit/mevduat gibi farklı araç türlerinden
oluşan portföyünün hedef ağırlıklardan ne kadar saptığını her gün otomatik
kontrol edip **e-posta** ile bildirim gönderen bot. **Emri kendin girersin** —
bot hiçbir aracı kurumda otomatik alım/satım yapmaz, sadece "şunu al / şunu
sat" sinyali üretir.

Portföyü düzenlemek için repo içindeki **web paneli** (`docs/index.html`)
kullanılabilir — GitHub'a girip YAML dosyasını elle düzenlemene gerek kalmaz.

## Desteklenen Araç Türleri ve Fiyat Kaynakları

| Tür | Kod formatı | Fiyat kaynağı |
|---|---|---|
| `fund` | TEFAS kodu (örn. SPT02) | TEFAS (pytefas) |
| `stock` | BIST kodu (örn. THYAO) | Yahoo Finance |
| `gold` | `GRAM` (sabit) | Ons altın (USD) x USD/TRY |
| `fx` | Döviz kodu (örn. USD, EUR) | Yahoo Finance |
| `crypto` | Kripto kodu (örn. BTC, ETH) | Binance (*TRY paritesi) |
| `cash` | Serbest etiket (örn. MEVDUAT1) | Sabit (1.0), `units` = doğrudan TL tutarı |

## 1. Gmail App Password Oluşturma

Gmail, normal şifrenle otomatik programların e-posta göndermesine izin
vermiyor; bunun için ayrı bir "Uygulama Şifresi" gerekiyor.

1. https://myaccount.google.com/security adresine git, **2 Adımlı
   Doğrulama**'nın açık olduğundan emin ol (kapalıysa önce onu aç).
2. https://myaccount.google.com/apppasswords adresine git.
3. Uygulama adı olarak "Fon Botu" gibi bir şey yaz, **Oluştur**'a bas.
4. Sana boşluklu 16 haneli bir şifre verecek (örn. `abcd efgh ijkl mnop`).
   Bunu olduğu gibi (boşluklarla) sakla — bu **GMAIL_APP_PASSWORD**'dür.

## 2. config.yaml'ı Düzenle

`config.yaml` dosyasını aç (ya da paneli kullan) ve:
- `instruments` altına her araç için **tür** (`type`), **kod**, **hedef
  ağırlık** (toplamları 1.0 etmeli) ve **elinde bulunan miktarı** (`units`)
  gir.
- Her alım/satım sonrası `units` alanını güncellemen gerekir (bot senin
  hesaplarına erişemediği için bunu otomatik bilemez).
- `rebalance` altında eşikleri istersen değiştir (varsayılan: 5/25 kuralı).

## 3. Yerel Test (opsiyonel ama önerilir)

```bash
cd fon_rebalance_bot
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını aç, GMAIL_ADDRESS, GMAIL_APP_PASSWORD ve EMAIL_TO'yu gir
python main.py
```

## 4. GitHub'a Yükleyip Otomatikleştirme

1. Bu klasörü kendi **private** bir GitHub reposuna yükle.
2. Repo → **Settings → Secrets and variables → Actions → New repository
   secret** ile şu üç secret'ı ekle:
   - `GMAIL_ADDRESS`
   - `GMAIL_APP_PASSWORD`
   - `EMAIL_TO` (virgülle ayrılmış birden fazla adres olabilir)
3. `.github/workflows/rebalance.yml` zaten hazır — her hafta içi günü
   20:00 (TR saati) otomatik çalışacak şekilde ayarlı.
4. Repo → **Actions** sekmesinden **"Run workflow"** ile manuel de
   tetikleyebilirsin.

## 5. Web Panelini Yayınlama (GitHub Pages)

1. Repo → **Settings → Pages**.
2. "Build and deployment" altında **Source: Deploy from a branch** seç.
3. Branch olarak **main**, klasör olarak **/docs** seç, **Save** bas.
4. Birkaç dakika sonra sayfanın üstünde bir link belirir (örn.
   `https://kullaniciadin.github.io/repo-adin/`) — bu senin panelin.

### Paneli Kullanma

1. Panel linkine git.
2. **GitHub Personal Access Token** oluşturman gerekiyor (her açılışta
   gireceksin, hiçbir yerde saklanmaz):
   - https://github.com/settings/tokens → **Generate new token (classic)**
   - "repo" kutucuğunu işaretle, süre seç, oluştur, token'ı kopyala.
3. Panelde Token, kullanıcı adı, repo adı ve dosya yolunu
   (`fon_rebalance_bot/config.yaml`, varsayılan olarak zaten dolu) gir,
   **Yükle**'ye bas.
4. Araç ekle/çıkar/düzenle, hedef ağırlıkların toplamı %100 olduğunda
   **Kaydet**'e bas — doğrudan GitHub'a commit edilir.

**Not:** Panel üzerinden kaydettiğinde `config.yaml` içindeki `#` ile
başlayan açıklama satırları kaybolur (YAML yeniden oluşturulduğu için),
sadece veriler korunur. Bu botun çalışmasını etkilemez.

## 6. Sorun Giderme

- **"için fiyat bulunamadı" hatası (fund):** Fon kodunu TEFAS'ta doğrula.
  `tefas.kind_overrides` içine örn. `{"AAK": "YAT"}` ekleyerek fon türünü
  sabitlemeyi dene.
- **Hisse fiyatı çekilemiyor:** BIST kodunu (örn. THYAO) doğru yazdığından
  emin ol, `.IS` eki kod tarafından otomatik ekleniyor.
- **Kripto fiyatı çekilemiyor:** Seçtiğin coin'in Binance'te doğrudan bir
  `*TRY` paritesi olmayabilir (örn. bazı küçük coinler sadece USDT
  paritesinde işlem görür). Bu durumda o coin için fiyat hatası alırsın.
- **E-posta gelmiyor / "Authentication failed":** Normal Gmail şifreni
  değil, App Password'ü kullandığından emin ol.
- **Panel "Yükle" hata veriyor (401):** Token'ın süresi dolmuş veya "repo"
  yetkisi işaretlenmemiş olabilir, yeni bir token oluştur.
- **Panel "Kaydet" hata veriyor (409):** Dosya panelde açıkken GitHub'da
  başka bir yerden değiştirilmiş olabilir (sha uyuşmazlığı). Sayfayı
  yenileyip tekrar **Yükle** yaptıktan sonra tekrar dene.
- **GitHub Actions çalışmıyor:** Actions sekmesinde workflow loglarına bak;
  secret isimlerinin `Settings → Secrets` içindekiyle birebir aynı olması
  gerekir (büyük/küçük harf dahil).

## Önemli Notlar

- Bu bot **yatırım tavsiyesi değildir**, sadece senin belirlediğin hedef
  ağırlıklara göre matematiksel bir sapma hesabı yapar.
- Fiyatlar genelde akşam saatlerinde netleşir; bot bu yüzden 20:00'de
  çalışacak şekilde ayarlandı.
- `units` alanını güncel tutmazsan hesaplamalar yanlış çıkar — en sık
  yapılan hata budur.
- Panel token'ı asla kaydetmez; her ziyarette yeniden girmen gerekir. Bunu
  değiştirmek istersen (tarayıcıda saklama) kodda küçük bir ekleme yeterli.
