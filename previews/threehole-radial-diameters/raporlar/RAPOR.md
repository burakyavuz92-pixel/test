# Çap lideri: sabit temas ve radyal dışa uzatma

Kayıtlı STEP ve model ölçü referansları ile yalnız 11-30-365 ve 11-30-260
paftaları yeniden üretildi. Yeni API çağrısı yok; STEP dosyalarının SHA256 değerleri
önceki çıktılarla aynı. Model kodu ve referansları değiştirilmedi.

- 11-30-365: 1:2, 8 ölçü, çözülemeyen/doğrulanamayan ölçü yok.
- 11-30-260: 1:4, 7 ölçü; F=0 gizli, E deliği korunuyor. Çözülemeyen/doğrulanamayan ölçü yok.
- İkisinde C/D/E inclined-diameter; aynı temas noktası/açı ile yalnız dışarı uzatma.
- 16 ölçü yerleşimi ve 8 ölçek testi geçti. Pah/radyus yerleşimi değiştirilmedi.

Çap yazısının tamamı görünüş kutusunun dışında aranır. Mesafe 8 piksel adımlarla
artırılır; temas ve radyal yön sabit kalır. Kısa/eğik olmayan lidere dönüş yok.
Uygun yer bulunamazsa ölçü yerleşim hatası raporlanır; ölçek seçici mevcut kontrollerle
başka ölçekleri deneyebilir. Antet, izometri ve sayfa sınırı kontrolleri korunur.

İki örnek görsel incelendi; rekor paftaları bu çalışmada yeniden üretilmedi.
