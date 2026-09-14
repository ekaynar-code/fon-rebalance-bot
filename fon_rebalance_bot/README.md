# Fon Rebalancing Sinyal Botu

TEFAS'taki fonlarının hedef ağırlıklardan ne kadar saptığını her gün otomatik
kontrol edip **e-posta** ile bildirim gönderen bot. **Emri kendin girersin** —
bot hiçbir aracı kurumda otomatik alım/satım yapmaz, sadece "şunu al / şunu
sat" sinyali üretir.

## 1. Gmail App Password Oluşturma

Gmail, normal şifrenle otomatik programların e-posta göndermesine izin
vermiyor; bunun için ayrı bir "Uygulama Şifresi" gerekiyor.

1. https://myaccount.google.com/security adresine git, **2 Adımlı
   Doğrulama**'nın açık olduğundan emin ol (kapalıysa önce onu aç).
2. https://myaccount.google.com/apppasswords adresine git.
3. Uygulama adı olarak "Fon Botu" gibi bir şey yaz, **Oluştur**'a bas.
4. Sana boşluklu 16 haneli bir şifre verecek (örn. `abcd efgh ijkl mnop`).
   Bunu olduğu gibi (boşluklarla) sakla — bu **GMAIL_APP_PASSWORD**'dür.
   Bu senin normal Gmail şifren DEĞİL, unutursan tekrar oluşturabilirsin.

## 2. config.yaml'ı Düzenle

`config.yaml` dosyasını aç ve:
- `funds` altına kendi fonlarının **TEFAS kodlarını**, **hedef
  ağırlıklarını** (toplamları 1.0 etmeli) ve **elinde bulunan pay adedini**
  (`units`) gir.
- Her fon alım/satımından sonra `units` alanını elle güncellemen gerekir
  (bot senin hesabına erişemediği için bunu otomatik bilemez).
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

E-postana mesaj geldiyse her şey doğru çalışıyor demektir.

## 4. GitHub'a Yükleyip Otomatikleştirme

1. Bu klasörü kendi **private** bir GitHub reposuna yükle (fon bilgilerin
   ve stratejin görünmesin diye private öneriyoruz).
2. Repo → **Settings → Secrets and variables → Actions → New repository
   secret** ile şu üç secret'ı ekle:
   - `GMAIL_ADDRESS`
   - `GMAIL_APP_PASSWORD`
   - `EMAIL_TO` (bildirimi almak istediğin adres(ler), Gmail adresinle aynı
     olabilir; birden fazla adrese göndermek istersen virgülle ayır, örn.
     `adres1@eposta.com,adres2@eposta.com`)
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
- **E-posta gelmiyor / "Authentication failed" hatası:** Normal Gmail
  şifreni değil, App Password'ü kullandığından emin ol. 2 Adımlı Doğrulama
  kapalıysa App Password oluşturamazsın, önce onu aç.
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
- İleride Telegram bildirimine geçmek istersen, `email_notify.py`'ın
  yanına aynı mantıkla bir `telegram_notify.py` eklemek yeterli.
