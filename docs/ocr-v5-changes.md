# OCR ilk tarama ve aday eşleme revizyonu

Uygulandı; kaynak JPEG'ler ve etiket biçimi değiştirilmedi. Yeni OCR motoru veya yeni API çağrısı eklenmedi.

- Görünüşlere göre ayrık kırpma yerine antet dışındaki çizim alanı taranır. Tam alan 15° adımlarla; bindirmeli iki yardımcı alan ana dört yönde taranır. Bu sabit ilk tarama planıdır, başarısız her etiket için tekrar deneme zinciri değildir. Ham/temizlenmiş varyantlar ve mevcut yerel kırpmalar korunur. Görünüş etiketi başlangıçta unassigned'dır; model referansı daha sonra atar.
- Yakın konumdaki farklı metinler erken elenmez. Aynı metnin tekrarları birleştirilir; farklı metinler observationGroup altında alternatif kalır. Böylece düşük güvenli doğru 5, yüksek güvenli 9 yüzünden kaybolmaz. Alternatiflerin varlığı onların çizim için onaylandığı anlamına gelmez.
- Modelin etiketi yalnız gözlenen aynı metinli adaya, görüntünün büyük boyutunun %2,5'i içinde bağlanır. Aynı fiziksel grup iki kez kullanılamaz. Eşleme yakınlığa dayalı sıralı seçimdir; genel en iyi küresel eşleme algoritması iddia edilmez.
- Eşleşmeyen/çakışan model etiketleri unconfirmedModelMarkers olarak tutulur; diğer etiketler devam eder. Bunlar yeni çizilebilir OCR adayları oluşturmaz. K gibi modelin ölçü etiketi vermediği geometri sütunları eksik listesine eklenmez.
- Her pafta unconfirmedVisualLabels listesini kaydeder. Ana akış bu liste doluysa sheets-produced-with-unconfirmed-labels / çıkış 2 üretir. Artık bilinen görsel eksikler tam başarı diye raporlanmaz. Doğrudan render-script-sheets komutu pafta raporunu üretir; genel durum kararı run/replay-cadquery-group tarafından verilir.
- Önbellek sürümü değiştirildi. Manuel sürüm dışında otomatik araç/kod parmak izi eklenmedi.

## Yerel karşılaştırma

| Örnek | Önce | Sonra |
|---|---|---|
| 6.4 | Akışta 7/11 gösterim yerleşti; C/E/2,8/25 kayıptı | 9/11 yerleşti; E ve 2,8 geri geldi. C ve Ø25 hâlâ doğrulanamadı |
| 6.5 | 7/11 tam OCR; C ve 5 yanlış 9; 2,8 kayıp; 25'in Ø işareti kayıp | On gösterimin doğru metinleri adaylarda korunuyor; C, 5 ve 2,8 geri geldi. Ø25 hâlâ yalnız sayı/tolerans olarak kısmi |

6.5 için yeni model çağrısı yapılmadığından tam pafta eşleme testi iddia edilmez. 6.4'ün model konumları değiştirilmiş 6.5'e otomatik taşınmadı. Ham adaylar yanlış alternatifler içerebilir; 6.5 sayımı, özgün JPEG'le karşılaştırılmış doğru metinlerin adaylarda varlığıdır, tüm adayların doğru olduğu anlamına gelmez.

İlk geniş-alan denemesi 6.4'te G'yi kaybettirdi; bunun üzerine sabit bindirmeli alanlar ilk taramaya eklendi ve iki örnek yeniden tarandı. Son 6.4 sürümünde önceki doğru yedi gösterim korunur. Bu, tek görüntüye bakıp gerilemeyi saklamak yerine karşılaştırmalı test yapmanın sonucudur.

Tam akış sınaması: 6.4 için yeni OCR ham kayıtları aynı kaynak hash'i ve önbellek sürümüyle standart cache'e kaydedilip kayıtlı model kodlarıyla replay çalıştırıldı. Böylece aynı tamamlanmış OCR taraması gereksiz tekrar edilmedi. Altı STEP/JPEG yeniden üretildi. Beş parça 1:1, kısa parça 2:1; her satırda 9 gösterim yerleşti, geometrik unresolved listesi boş, görsel unconfirmed listesinde C ve Ø25 var. K geometri verisidir ve çizimde yoktur. API çağrısı 0.

## Sınırlar

Çizgi temizleme, sınırlı karakter kurtarma ve sabit piksel eşikleri hâlâ mevcut; tüm OCR riskleri çözülmüş değildir. C'nin 6.4'teki kırık kapanış okuması ile Ø gibi simgeler hâlâ iyileştirme gerektirir. OCR ve modelin ikisinin de hiç fark etmediği bir gösterimi bu rapor kendiliğinden keşfedemez. Geometrinin taslağa tam uygunluğu bu testin konusu değildir.
