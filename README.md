# DrawingTool — parametrik CAD tarifi ve OCCT

Girdi **bir taslak JPEG + bir Excel**. Yazılım Excel'i yerelde ayrıştırır; OpenRouter'a **tek JPEG ve tek ayrıştırılmış örnek satır tablosu** gönderir. Geometri nominal değerleri kullanır; toleranslar ölçülendirmede korunur. Bütün Excel satırları aynı parametrik tarifle yerelde işlenir. Büyük tablolarda modele en fazla sekiz temsilci satır gönderilir.

## Etkin model ayarları

[config/openrouter.json](config/openrouter.json) etkin CAD akışının ayar kaynağıdır:

- Model: `anthropic/claude-haiku-5.5`
- Reasoning: `high` (renk takibi olmadan Haiku denemesi)
- Completion token sınırı: `65536` (görünür çıktı ve reasoning toplamı için tavan)
- HTTP zaman aşımı: `600` saniye

Dosyada API anahtarı bulunmaz. Anahtar yalnız `OPENROUTER_API_KEY` ortam değişkeninden okunur. Eski `OPENROUTER_MODEL`, `OPENROUTER_REASONING_EFFORT`, `OPENROUTER_MAX_COMPLETION_TOKENS` ve `OPENROUTER_TIMEOUT_SECONDS` ortam seçimleri etkin CAD akışını değiştirmez; model/ayar değişikliği bu JSON dosyasından yapılır. Dosya yoksa kod varsayılanları kullanılır; reasoning varsayılanı high kalır.

Batch gönderme ve sorgulama yolu kaldırıldı. `:batch` model kodu yerelde reddedilir. Tek normal istek yapılır; hata veya zaman aşımında otomatik yeniden değerlendirme/tekrar gönderim yoktur. Başarı yalnız veri, model hatası kısa cümle olarak alınır. Yazılım kullanıcıdan cevap beklemek yerine rapor kaydeder.

## Yerel çizim düzeni

Revize Excel'de `izometrik aci`, `kesit dogrultu`, `kesit kacikligi`, `kacik kesitin genisligi` sütunları bulunur. Bunlar modele gönderilmez; kamera ve kesit yazılımda uygulanır. Başlıklar, işaretler ve birimler için [kullanım notları](docs/local-drawing-settings.md).

Bu akışın model dosyaları:

- [local-prompt.txt](contracts/cad-v9-draft/local-prompt.txt)
- [local-contract.txt](contracts/cad-v9-draft/local-contract.txt)

Sözleşme `schemaVersion:9`, `geometry` ve `drawing` içerir. Model tek gövdede parametrik ekleme/çıkarma, döndürme, ekstrüzyon ve radyus/pah işlemleri tarif eder. `drawing` yalnız ölçü ilişkileri ve geometrik toleransları ister. Kamera, kesit, pafta yerleşimi ve görünürlük tarifi istenmez. Etkin sözleşmede renk alanı istenmez. Ölçüler renk ayrımı olmadan geometri için kullanılır. Görünürlük için Excel düzeni henüz eklenmediğinden renk alanı bulunmayan ölçüler gizlenmez; eski renkli yanıtların okunması korunur.

Üst yüzey merkezi orijindir; +X sağ, +Y yukarı, +Z üst yüzeyin dışıdır; gövde -Z yönüne uzanır. Yerel koordinat düzeninde hazırlanmış tarifler eski, modelin seçtiği koordinatlardaki tariflerden ayrı tutulur. Eski kaydı yeni düzende otomatik kullanmak yerine yeni analiz gerekir. Kayıtlı tarihsel tariflerin yerel inceleme yolu korunur. Yeni API analizleri yerel ayar sütunlarını gerektirir; eski prompta otomatik dönüş yapılmaz. Eski prompt/sözleşme dosyaları yalnız tarihsel referanstır.

## Çalıştırma

Komutları depo kökünden çalıştırın. Çıktı klasörü yeni veya boş olmalıdır.

```bash
# Tek API isteğiyle yeni tarif; ardından bütün satırlarda yerel OCCT üretimi:
dotnet run --project src/DrawingTool.csproj -- run-fresh-cad-group input.xlsx template.jpg output/new-run

# Yalnız tarif analizi (API çağırır):
dotnet run --project src/DrawingTool.csproj -- analyze-fresh-cad-group input.xlsx template.jpg output/new-analysis

# Kayıtlı, aynı Excel/JPEG ile üretim (API çağırmaz):
dotnet run --project src/DrawingTool.csproj -- render-saved-group input.xlsx template.jpg output/new-analysis output/local-render
```

`run-cad-group` ve `analyze-cad-group` aynı akışın onaylanmış tarif kütüphanesini kullanabilen karşılıklarıdır. Model çıktısı ham haliyle saklanır; satır başına çözümleme ayrı kaydedilir. CPU ile OCCT üzerinden STEP ve JPEG üretilir; STEP yeniden okunarak katı bütünlüğü kontrol edilir. Anahtar ve özel font dosyası depoya eklenmez. `OCCT_PYTHON` yerel OCP/VTK/Pillow içeren Python yürütücüsünü seçer; bulutta varsayılan `/workspace/occt-venv/bin/python` kullanılır. Arial yerel kurulumdan sağlanır.

## Mevcut çıktı sınırı

Genel v9 çıktısı **inceleme paftasıdır**. OCCT geometrisi, kesit ve izometrik görüntü üretilir; fakat taslaktaki antet/yerleşim birebir yeniden kurulmaz, ölçüler oklar üzerinde değil tabloda gösterilir. Tam teknik resim yerleşimi ve eksen çizgileri tamamlanmış sayılmaz. JPEG boyutu 1754×1240, DPI metadata'sı kaynaktandır; bu tek başına gerçek baskı ölçeğini garanti etmez. Modelin görsel yorumu insan kontrolü gerektirir.

## Kontroller ve kayıtlar

```bash
dotnet build src/DrawingTool.csproj
dotnet run --project checks/LayoutPolicyChecks.csproj -- samples/local-settings-rev/taslak4.2rev.xlsx
python -m unittest discover -s tools -p 'test_local_drawing.py'
python -m unittest discover -s tools -p 'test_cad_v9.py'
python -m unittest discover -s tools -p 'test_cad_recipe_executor.py'
```

Python testleri için OCP/VTK/Pillow içeren ortam kullanılır. Bu kontroller API çağırmaz. Derleme ve yerel testlerin geçmesi, yeni promptla model yorumunun doğrulandığı anlamına gelmez.

`request-prompt.txt`, `model-input.json`, `normalized-excel.json` istek içeriğini; `local-drawing-settings.json` yerel ayarları; `run-report.json` kullanım ve hata durumunu; `native-drawing.json` native kesit çözümünü kaydeder. Modelin özel akıl yürütmesini içerebilen ham `api-response.json` yayımlanmaz.
