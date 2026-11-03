# JPEG + Excel → CadQuery → STEP + pafta

Depo kökünden, CadQuery 2.6.1 ve OCP/Pillow/VTK/OCR ortamları hazırken:

```bash
export CADQUERY_PYTHON=/workspace/cq-experiment-venv/bin/python
export OCCT_PYTHON=/workspace/occt-venv/bin/python
export DOTNET_CLI_HOME=/workspace/.dotnet-home
export NUGET_PACKAGES=/workspace/.nuget/packages
/workspace/.dotnet/dotnet run --project src/DrawingTool.csproj -- run-cadquery-group input.xlsx template.jpg output/new-run
```

Çıktı klasörü yeni/boş olmalıdır. Anahtar OPENROUTER_API_KEY olarak ortamdan alınır. Model, reasoning, token sınırı ve zaman aşımı config/openrouter.json dosyasından okunur. İlk çağrı parametrik geometriyi üretir. Bütün satırlarda geometri üretimi başarılıysa ikinci çağrı aynı geometriye bağlı ölçü fonksiyonunu ve görsel işaretleri üretir. Otomatik API tekrar çağrısı yoktur. Geometri başarısızsa ikinci çağrı yapılmaz. Canlı akış iki çağrı kullanır; STEP'i model değil CadQuery/OCCT yazar.

Aşamalar: Excel/yerel ayarlar → geometri çağrısı → kontrollü script ve STEP üretimi → ölçü çağrısı → kontrollü ölçü fonksiyonu → OCR parantez filtresi ve geometri doğrulaması → ölçü şeritleri, antet, JPEG/PDF. Her aşamada log ve rapor tutulur. Bir satırda geometri hatası varsa pipeline o aşamada durur; oluşmuş diğer dosyalar korunur. Paftalarda çözülememiş ölçü varsa durum sheets-produced-with-unresolved-measurements ve çıkış kodu 2'dir; kusursuz başarı sayılmaz.

## Tek zinciri API olmadan yeniden doğrulama

```bash
/workspace/.dotnet/dotnet run --project src/DrawingTool.csproj -- replay-cadquery-group input.xlsx template.jpg output/saved-script output/new-replay
```

Kayıtlı klasör part.py, measurements.py, visual-markers.json içermelidir. Fonksiyonlar tekrar çalıştırılır; geometri ve paftalar sıfırdan üretilir. API kullanımı sıfırdır. Bu mod canlı modelin yeni girdiyi doğru yorumlayacağını kanıtlamaz; aşama bağlantısını doğrular. Tekrarda aynı input dosyaları kullanılmalıdır; tarihsel deney klasörlerinin kaynak manifesti yoksa arşiv uyumu kullanıcıya aittir. Yeni pipeline koşuları JPEG/Excel SHA256 manifesti üretir; pafta aşaması farklı girdiyle kullanımı reddeder.

## Ölçek

Ana görünüş ve kesitin geometrik en/boyu, kendi panel alanlarına 30 piksel pay bırakılarak sığdırılır. İki görünüşe uyan en büyük hazır ölçek seçilir ve ikisi aynı ölçeği kullanır. Liste: 1:1, 1:1,25, 1:1,5, 1:2, 1:2,5, 1:3, 1:4 vb.; büyütme de mümkündür. Uygun hazır değer bulunamazsa sığan sayısal oran kullanılır. Ölçek antette yazılır. İzometri ayrı ve ölçeksizdir. PDF fiziksel A5'tir; baskı %100 olmalıdır. Ölçü şeritlerinin toplam alanı ölçek kararına henüz dahil değildir.

## Doğrulanan kapsam

Taslak4.7'nin altı satırı kayıtlı API yanıtlarıyla tek komuttan tekrar üretildi; altı STEP ve JPEG/PDF, sıfır çözülememiş aktif ölçü. Derleme, 20 ilgili Python testi ve yanlış JPEG kaynak kontrolünün reddi doğrulandı. Yeni iki-aşamalı canlı prompt zinciri bu test sırasında ücretli API çağrısıyla yeniden sınanmadı. Genel geometri desteği için önceki testlerin ve farklı taslak denemelerinin sınırları geçerlidir.
