# CAD v8 — bağımsız değerler içeren JSON tarifi

Modelin çıktısı betik değildir. Bir ürün grubuna bir parametrik JSON tarifi gelir; tüm Excel satırlarını yerel yazılım uygular. Başarı: yalnız veri. Başarısızlık: `{"error":"kısa cümle"}`. Tam alan sözlüğü `src/CadRecipePrompt.cs` içinde tutulur.

V7'den farkları:

- Model parametre veya aritmetik bağımlılık listesi üretmez. Her sayısal alanda doğrudan sayı, `{"column":"A"}` veya `{"expr":"A / 2 - 3"}` kullanır. Tekrar serbesttir. İfadeler yalnız sütunlar, ondalık sabitler, dört işlem ve parantez içerir; kod çalıştırılmaz.
- İşlemlerde sıralı `uses` yerine `body`, `tool`, `sketch`, `seed`, `additions` alanları vardır. Şekillerin birbirine bağlanması için ID'ler korunur.
- `world` bazı yerelde sağlanır. İlave bazlar isteğe bağlıdır.
- Geometri yalnız nominal değer kullanır. Ölçülendirme `valueSource` ile kaynak sütunun toleransına veya sabit değere bağlanır. Aynı bilgiyi iki bölümde yeniden yazmak yasak değildir.
- Kesit, detay, görünüş ve ölçülendirme kapsamı korunur. Modelden açıklama, kanıt, rapor veya en kısa işlem ağacı istenmez.

`CadRecipeV8` her satırda ifadeleri hesaplar ve mevcut özel yürütücü yapısına dönüştürür. V7/V6 iç yapıları geriye uyumluluk ve yerel yürütme için kalır; yeni API isteğinde gösterilmez. Ham `recipe.json` değiştirilmez. Çözülmüş dosyaların iç yürütücü sürümü 7 olabilir; bu API sözleşmesinin 8 olmadığı anlamına gelmez.

Boş hücre kullanan aktif ifadeler, bilinmeyen sütunlar, geçersiz aritmetik ve sıfıra bölme raporlanır. `columnPresent` ile pasif olan özelliğin boş ifadesi hesaplanmaz. Sayısal sıfır boş sayılmaz. Alanların birimleri sözlükte belirlenir; yeni ifade çözümleyicisi bağımsız bir boyut cebiri doğrulayıcısı değildir.

Bu değişiklik modelin düşünme maliyetini düşüreceği garantisi taşımaz. Testte aynı kaynaklar/model/high seviyesi ve tam tarif kapsamı korunarak kullanım karşılaştırılır. BRep geçerliliği parçanın taslakla eşleştiğinin kanıtı değildir. Mevcut native önizleme hâlâ üretim paftası değildir; antet, ölçü okları ve taslak yerleşimi tamamlanmış sayılmaz.
