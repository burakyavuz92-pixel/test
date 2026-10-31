# Taslak4.2 — NVIDIA Nemotron denemesi

Model: nvidia/nemotron-3.5-super-vl. Kullanıcının yapılandırdığı model mevcut v9 yazılımıyla denendi. Aynı JPEG, Excel, tam metin girdisi ve sözleşme önceki Claude denemesiyle birebir eşleşiyor. İstekte reasoning effort=high ve aynı completion sınırı gönderildi; modellerin high ayarının aynı hesaplama bütçesi olduğu varsayılmıyor. Tek API çağrısı. Ham model tarifi değiştirilmedi, yazılıma müdahale veya otomatik onarım çağrısı yapılmadı.

## Kullanım

| Kullanım | Önceki Claude Sonnet 5.5 | Nemotron |
|---|---:|---:|
| Input token | 9825 | 6578 |
| Reasoning token | 9786 | 24409 |
| Görünür completion (completion−reasoning) | 3167 | 784 |
| Toplam completion | 12953 | 25193 |
| USD | 0,149180 | 0,0139121 |
| Cache token | 0 | 0 |

Komut başlangıcından API yanıtının dosyaya kaydına yaklaşık 62 saniye; salt reasoning süresi değildir. Metin aynı olmasına rağmen input token sayıları farklı; model tokenizer/görüntü hesaplama farkları nedeniyle sayılar doğrudan aynı iş miktarını ölçmez. Birim fiyatları farklıdır: maliyet yaklaşık %90,7 düşük. Bu doğruluk kazancı değildir.

## Çıktı başarısız: farklı bir parça tarif edildi

Yazılım üç geçerli tek katı, STEP yeniden okuma kontrolü ve üç JPEG inceleme önizlemesi üretti. Ancak modelin yorumu taslakla örtüşmüyor:

- Kap biçimli 3 mm cidarlı, 33 mm derinlikli gövdeyi kurmadı. A çaplı, E kalınlıklı düz disk yaptı.
- B ofsetini merkezdeki yükseltilmiş yüz çapı olarak kullandı; B>0 koşuluyla ekledi. B=0 satırında bu özelliği kaldırdı.
- C aralığını hatve çemberi gibi yorumladı; J çapında dört çevresel delik üretti. Taslakta böyle bir dört delik düzeni yok.
- D'yi merkez açıklığı çapı yaptı. G ve I delik çapları geometri tarifinde kullanılmadı.
- R8, R1,5, R2, J+6 ve 33/3 sabit gövde bilgileri uygulanmadı.
- F içe boşaltma olarak kullanılmadı; merkez yükseltisi yüksekliği yapıldı.
- Bazı çap ölçülerinde zorunlu axis alanı da eksik; mevcut yerel çözümleyici bunu reddetmedi. Yapısal doğrulama eksikliği ve BRep kontrolünün taslak doğruluğunu kanıtlamaması ayrıca görülüyor. Bu çalışmada kod değiştirilmedi.

Bu yorum raw recipe.json içinde bulunuyor; yazılımın farklı bir gövde üretip modeli değiştirmesi söz konusu değil. Geometrik geçerlilik taslağı doğru anlamak değildir. Bu ayar/örnekte Nemotron başarılı sayılmaz; bütün NVIDIA modelleri hakkında genelleme yapılmaz. JPEG'in sağlayıcı/model içinde nasıl işlendiği bu denemeden belirlenemez.

Dosyalar hatayı incelemek için yayımlanmıştır; üretim için uygun değildir. Önceki antet/ölçü okları gibi yerel inceleme paftası sınırlamaları da sürer.
