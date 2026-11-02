# Taslak4.4rev — aynı algoritmayla karşılaştırma

Zip yalnız taslak4.4rev.jpg içeriyor. Önceki taslak4.4.xlsx sütun eşleştirmesinde kullanıldı. Algoritma değiştirilmeden inspect_bracket_layout.py çalıştırıldı. API çağrısı ve ürün çizimi yok. Konumlar elle tamamlanmadı.

8 aday bulundu: B/C ana görünüşte; A/D/E/F, 3 ve R2 kesitte. Excel etiketlerinden 6/10 bulundu. Eski taslakta 9/10 bulunmuştu. Yeni JPEG'de K parantezsiz görünüyor; kurala göre işaretlenmedi. G/I/J ise parantezli olmalarına rağmen OCR tarafından kaçırıldı. Bu yüzden toplam 4 eksik etiketi aynı tür hata gibi değerlendirmemek gerekir. K'nin parantezsiz oluşunun kullanıcı niyeti olduğu varsayılmadı.

Etiketleri yalınlaştırmak bu mevcut okuyucuda tek başına başarı artışı sağlamadı. D'nin OCR güveni de düşük (yaklaşık 28); kayıtların tamamı needs-review durumundadır. Kutular görsel incelendi. Parantezsiz R5/R8/R1,5 yerleşim etiketi olarak alınmadı. Tespit sonucu üretim yerleşimine bağlanmadı.

Bu bir başarısızlık gizleme veya eksikleri tahminle doldurma denemesi değildir. Sonraki geliştirmede G/I/J için etiket ve parantezleri ayrı bulma, alt çizgi temizliği ve karakter tanımayı iyileştirmek gerekir; kullanıcıdan tekrar tekrar taslak değiştirmesini istemeden bu dosya regresyon örneği olarak tutulmalı.
