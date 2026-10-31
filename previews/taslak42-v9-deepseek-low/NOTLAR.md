# Taslak4.2 — DeepSeek low denemesi

Model deepseek/deepseek-v4.1-flash-1017, provider=Relace. high yerine süreç için OPENROUTER_REASONING_EFFORT=low seçildi. Aynı orijinal JPEG, Excel, tam metin girdisi, sözleşme ve 32768 toplam completion sınırı korundu. Görsel küçültülmedi. Tek API çağrısı; yazılım/prompt değişikliği, elle tarif düzeltmesi ve otomatik onarım çağrısı yok.

| Ölçüm | High | Low |
|---|---:|---:|
| Input | 4191 | 4191 |
| Reasoning | 31548 | 22420 |
| Toplam completion | 32768 | 25484 |
| USD | 0,016530685 | 0,012888685 |
| finish_reason | length | stop |

Yanıt dosyasına kadar yaklaşık 139 saniye; high 226 saniyeydi. Bunlar salt düşünme süreleri değil. Low maliyeti yaklaşık %22,0 azaltmış; reasoning yaklaşık %28,9 düşük. Cache 0. Low yine de sabit düşük token sayısı garantisi değildir.

## Yanıt tamamlandı ama çizime geçilemedi

Bu kez JSON geçerli ve tamamlanmış. High denemesinde content null idi; low yanıtında görünür tarif mevcut (completion−reasoning=3064). Ancak sourceView=side ve view=side olarak aynı görünüş seçilmiş; kaynak ve kesit yönleri [1,0,0] olduğu için featureTrace diklik kontrolü üç satırda da durdurdu. Ham veri korunarak modelin referansları elle düzeltilmedi. Native katı/çizim üretimi başlamadı; STEP/JPEG yok.

## Geometri ayrıca yanlış

- Kaynak kap biçimli gövde yerine E kalınlığında A çaplı düz disk tarif etmiş; 33 derinlik/3 cidar/R8/R1,5 profili yok.
- B'yi ofset yerine merkezî çıkıntı boyu, C'yi delik aralığı yerine çıkıntı çapı yapmış. B=0 satırında çıkıntıyı kaldırıyor.
- Yan delikleri x=±(A+C)/4 yerleştirmiş; kaynak y=±C/2 ilişkisini korumamış.
- F'yi yerel boşaltma yerine dış disk kenarı pahı olarak kullanmış.
- R2 ve J+6 bilgisi uygulanmamış; renk/ölçü türlerinde de yanlış eşlemeler var.

Bu sonuç yalnız kesit adaptörü düzeltilerek doğru parçaya dönüşmez. Modelin temel geometri yorumunun taslakla örtüşmediği ham tariften görülüyor. Low ile yanıt tamamlanabilmiş olması başarı sayılmadı; görsel doğruluk doğrulanmadı. Kayıtlı model tarifi recipe.json içinde incelenebilir; gizli reasoning metni yayımlanmadı.
