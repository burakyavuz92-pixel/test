# Taslak6.5 — kod değiştirmeden OCR denemesi

Orijinal JPEG değiştirilmedi. Mevcut `inspect_bracket_layout.py` varsayılanlarıyla çalıştırıldı; aynı arşivdeki Excel'in adı taslak6.4.xlsx olduğundan etiket sözlüğü için bu dosya kullanıldı. Kod/ayar değiştirilmedi; dört ilgili kaynak dosyanın öncesi/sonrası SHA256 özeti `summary.json` içinde eşitlik kontrolünden geçti. Ek karşılaştırma: JPEG doğrudan Tesseract `--psm 11 -l eng tsv` ile, kırpma/temizleme/döndürme olmadan okundu. API çağrısı yok.

## Mevcut OCR akışı

| Kaynak | Sonuç |
|---|---|
| A, B, D, E, F, G, J | Doğru yakalandı |
| C | Kaynak konumunda 9 olarak yanlış aday var; C bulunmadı |
| 5 | 9 olarak yanlış kabul edildi |
| 2,8 | Bulunamadı |
| Ø25 ±0,5 | Sayı ve tolerans 25±0,5 bulundu; Ø kayıp, tam doğru değil |
| K | Köşeli parantezsiz; bilinçli olarak ölçü etiketi değil |

Bu 11 gerçek ölçü gösteriminden 7'sinin tam, 1'inin kısmi, 2'sinin yanlış okunması ve 1'inin kaybı demektir. Antetteki [H] ölçü sayılmadı. Toplam aday sayısı doğruluk sayısı değildir: iki yanlış 9 adayı da sonuç listesine giriyor.

## Ham kayıtlarda görülenler

- C tam görüntü Tesseract çıktısında `[C]`, güven 91.642822. Mevcut kesit kırpmasının 0° ham/temizlenmiş okumalarında `[C.` (64.535286 / 59.979534). Başka açıdaki `[9]`, C'nin konumunda (yaklaşık [1995,1559]) kabul edilmiş. C'nin yalnız kaynaktan dolayı okunamadığı sonucu çıkarılamaz; kırpma/segmentasyon akışı fark yaratıyor.
- 5 için ana ön görünüş ham okuması `[9]`, güven 93.064087; yerel kırpma `[5]`, güven 34.354156. Son aday seçiminde yüksek güvenli 9, doğru 5'i kaybettirmiş.
- E bu sürümde `[E]`, güven 67.3 ile doğru. Önceki sürümdeki E→J değişimi burada tekrarlanmadı.
- 25'in 315° ham okuması `[25` ve `+0,5]`; mevcut piksel tabanlı ± normalizasyonuyla 25±0,5 olmuş. Ø ham metinde yok. Düşük güvenli 35.1 aday üzerinden tam başarı iddia edilemez.
- 2,8 mevcut kırpma bölgelerinin sınırına yakın; bu çalışmada tam etiket oluşmadı. Bu sonuç tek başına hangi ön işleme ayrıntısının son kayba neden olduğunu kesinleştirmez.

## Doğrudan tam JPEG denemesi

Tam köşeli parantezli ham okumalar: `[C]`, `[9]`, `[D]`, antette `[H]`. 9, kaynakta 5 olan konumda. Bu tek, döndürülmemiş genel okuma; mevcut çok açılı akışla aynı işlem değildir. Döndürülmüş yazılarda tek başına yeterli olmadığı görülüyor.

Kod değiştirmeme isteği nedeniyle hiçbir normalizasyon veya aday seçimi düzeltmesi uygulanmadı. `detection-preview.jpeg` yalnız mevcut programın bulduğu adayların işaretlendiği teşhis önizlemesidir; orijinal JPEG'in yerine kullanılmadı. `ocr-evidence.zip` mevcut ham açı/variant kayıtlarını içerir.
