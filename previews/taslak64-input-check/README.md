# Taslak6.4 akış denemesi — giriş aşamasında durdu

Mevcut yazılım değişiklik yapılmadan run-cadquery-group ile çalıştırıldı. İlk hata: `733001 / F: Desteklenmeyen ölçü/tolerans biçimi: 1x45°`. Aşama `input`; API çağrısı 0, token 0, maliyet 0. STEP veya çıktı JPEG üretilmedi. Önceki sürümlerin çıktıları yeni çıktı gibi sunulmadı.

## Girişte görülen değişiklikler

- Altı satır ve A/B/C/D/E'ye ek F/G/J/K ölçü sütunları var.
- F=1x45°, G=1x45°, J=3x35°. Bu değerler ana geometri hücrelerinde. JPEG sabit pah ifadesi ve model pah kaydı desteği mevcut, ancak Excel ana hücresinde boy+açı birleşimi henüz desteklenmiyor. Sorun modelden önce oluşuyor.
- K=9,5; çizimde K köşeli parantezsiz. Mevcut kurala göre geometriye bilgi sağlayabilir ama otomatik ölçülendirme için onaylanmış etiket sayılmamalı.
- E bütün satırlarda Ø20,9. 733001-03 D=16.
- Kaynakta [5] ve [2,8] ölçüleri parantezli. Sağ pah G, sol iç pah F, sol dış pah J ile ayrı verilmiş. Montaj oku ve 25 gösterimi var.

Sonraki gerekli geliştirme: Excel'deki pahın boyunu ve açısını birbiriyle ilişkili, birimleri belirli geometri verisi olarak ayrıştırmak; her iki değeri de modele ve aynı satırın referans değerlendirmesine kayıpsız aktarmak. Açıyı yok sayarak veya pahı sadece gösterim metnine çevirerek bu engel aşılmış sayılmaz. Kullanıcı dosyası bu testte değiştirilmedi; API'nin yeni taslağı nasıl yorumladığı henüz denenmiş değildir.
