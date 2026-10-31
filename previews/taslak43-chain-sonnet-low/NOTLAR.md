# Aynı koşullarda Sonnet 5.5 low

Aynı JPEG, Excel ve sözleşme kullanıldı; gönderilen prompt high denemesindekiyle bayt bayt aynı. Yalnız reasoning low yapıldı. Token tavanı 65536 ve zaman aşımı 600 saniye aynı. Tek API çağrısı, yanıt elle değiştirilmedi. 3 JPEG ve 3 STEP üretildi.

| Kullanım | High | Low |
|---|---:|---:|
| Input | 9188 | 9188 |
| Reasoning | 7285 | 1002 |
| Görünür çıktı | 2039 | 1193 |
| Toplam completion | 9324 | 2195 |
| Maliyet USD | 0,111616 | 0,040326 |

İki denemede de cached input 0. Maliyet yaklaşık %63,9 düştü.

Low tarifinde D/F boşaltması ve R2 yok; bu ölçüler ölçü tablosunda da bulunmuyor. Dış R8 filleti var, fakat high profilindeki iç geçiş radyusu ve kenar R1,5 işlemi tarif edilmedi. Hub -2 noktasından E+2 boyuyla -E-4 konumuna uzanıyor; E üst yüzden toplam mesafeyse 4 mm fazla. C bu kez siyah döndü ve tabloda görünüyor.

İlk JPEG incelendi. Dosyaların oluşması bütün ölçülerin uygulanmış olduğu anlamına gelmiyor. Low bu tek örnekte daha ucuz fakat eksik tarif üretti. Kaliteyi koruduğu söylenemez. İnceleme paftasının antet, ölçü oku ve kesit sınır çizgisi eksikleri devam ediyor.

Proje ayarı bu deneme sonunda low olarak bırakıldı. Bu bir kalite önerisi değil, son denenen ayarın kaydıdır.
