# API için temsilci satır seçimi

`run-cadquery-group` iki çağrı için aynı temsilci tabloyu kullanır. Tam tablo
`rows.json` ve `normalized-excel.json` içinde kalır; bütün ürünler yerelde yürütülür.
Otomatik ek API çağrısı veya tekrar eklenmemiştir.

Politika: `coverage-and-numeric-diversity-v1`.

- Nominal değer, boş/sıfır durumu, çap/radyus sembolü ve pah açısı aynı olan
  satırlar örnek seçiminde birleştirilir. Ürün kimliği, tolerans ve baskı metni
  geometri örneğini çoğaltmaz; asıl çıktılar ayrı üretilir.
- En fazla 12 satırlı gruplarda benzersiz örneklerin tamamı seçilir.
- Daha büyük gruplarda açılar, boş/sıfır durumları, her sayısal parametrenin
  minimum/maksimum/en küçük pozitif değeri ve parametre çiftlerinin küçük/eşit/büyük
  durumlarını kapsayan satırlar açgözlü kapsama seçimiyle alınır.
- Sonra normalize sayısal uzayda mevcut seçime en uzak satırlar ile 12'ye tamamlanır.
  Eşitlikler özgün satır sırasına göre çözülür. Zorunlu kapsama 12'yi aşarsa örnek
  sayısı artırılır; nadir bir durum sayısal kota için atılmaz.
- `sampling-report.json` seçilen kimlikleri, kapsadıkları durumları, eşdeğer
  kimlikleri ve tam/seçilmiş model tablosunun UTF-8 bayt boyutlarını kaydeder.
  Bayt sayısı token sayısı değildir.

Sayısal ilişkiler genel kapsama göstergeleridir; taslağın geometrik anlamını
çözmez, gelecekteki satırlar için eşitlik veya oran kuralına dönüşmez. Her ara
sayısal değerin veya olası kombinasyonun örneklenmesi garanti edilmez. Modelin
incelemediği satırdaki çelişki, ancak üretilen kod/yerel kontroller yakalarsa rapora
yansır. STEP geçerliliği taslağa tam geometrik uygunluğu tek başına kanıtlamaz.

Kontrol: `dotnet run --project checks/SamplingChecks.csproj`.
Gerçek çalışma kitabından alınan nominal değerler `checks/fixtures/threehole-nominal.json`
içinde taşınabilir test girdisi olarak saklanır. Yapay kontroller sıfır/boş ayrımı, ilişki değişimi, pah açısı,
tekrarlanabilirlik, nominal tekrarlar ve yumuşak kota davranışını sınar.

## Çıktı klasörü

Yeni canlı/tekrar koşularında bütün nihai `ürün.step` ve `ürün.jpeg` dosyaları
seçilen çıktı klasöründe birlikte bulunur. Kayıtlar, model betikleri, OCR ve diğer
ara dosyalar tek `raporlar/` alt klasöründedir. Bu klasör teknik çalışma kayıtlarını
ve yeniden inceleme için ürün başına ara kopyaları da tutar.
Geometri önizlemesi, ölçülendirilmiş JPEG yerine ana klasöre çıkarılmaz. Pafta
üretilemese de oluşmuş STEP dosyaları korunur; hata ayrıntıları `raporlar/` içindedir.
`replay-cadquery-group` eski kayıt klasörlerini ve yeni ana çıktı klasörünü kabul eder;
yeni düzende betikleri otomatik olarak `raporlar/` içinden okur.
