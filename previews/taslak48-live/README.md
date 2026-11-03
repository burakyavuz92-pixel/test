# Taslak4.8 — baştan canlı Haiku 5.5/high denemesi

JPEG ve Excel girişten verildi. İki canlı API çağrısı yapıldı. Üretilen geometri ve ölçü kodları elle değiştirilmedi.

- Altı satırda tek geçerli katı, STEP dışa aktarım ve yeniden okuma/hacim doğrulaması geçti.
- Yüz etiketi aşamasında model z=-3 düzlemini doğru seçti; ancak örnek noktayı bütün satırlarda sabit [0,-97,-3] verdi. 11-24-13 ve 11-80-13 STEP dosyalarında montaj etiketi geri okuma doğrulandı. Diğer dört STEP'te bu nokta yüz dışında olduğundan etiketleme reddedildi. Bu dosyalar montaj etiketi varmış gibi kullanılmamalı.
- Ana pipeline bu nedenle failed döndü; hata durumu korunmuştur.
- Pafta aşaması teşhis amacıyla ayrıca çalıştırıldı: altı JPEG ve sıfır çözülememiş aktif ölçü. Bu, bütün geometri yorumunun doğru olduğunu kanıtlamaz. Yeni model kodu önceki 4.7 kodundan farklıdır; R2 işlemi bu kez çıkıntının serbest uç kenarına uygulanmıştır. Önceki kullanıcı geometrik onayı bu yeni koda taşınamaz.
- Toplam iki çağrı maliyeti 0,0417894 USD. Yeni model denemesiyle otomatik onarım/tekrar yapılmadı.

Paket yalnız STEP/JPEG ve kısa doğrulama raporları içerir; ham API yanıtı veya reasoning metni içermez.

[Sonuç ZIP](taslak48-live-step-jpeg.zip)

## Güncel yüz seçimi

Tek bir yüzü belirleyen geometrik düzlem/silindir tanımı için nokta zorunluluğu kaldırıldı. Aynı kayıtlı model tanımlarıyla, geometri değiştirilmeden altı STEP'in tamamına montaj adı yazılıp geri okunarak doğrulandı. Bu yerel doğrulama düzeltmesidir; yeni API çağrısı yapılmadı. Eski run-report.json ilk canlı denemenin başarısız tarihsel kaydıdır. Güncel etiket sonucu face-tag-results.json içindedir.
