# Notsuz taslak2guncel — genel CAD v5 analizi

Aynı kırmızı talimatları silinmiş taslak2guncel-notesiz.jpg ve dört satırlık taslak2guncel.xlsx normal v5 analiz komutuna verildi. Görüntünün SHA256 özeti önceki notsuz denemeyle aynı. high akıl yürütme, tek API çağrısı. Yeni çizim/STEP yok. Modelin tarifi elle değiştirilmedi, yeniden değerlendirme çağrısı yapılmadı.

## Doğru tarif edilenler

19 parametre ve 8 işlem döndü. A dış çapı, sabit 33 derinlik/3 et kalınlığı/R8 büküm tanındı. İç çap A-2t, iç boşluk derinliği 33-t, iç büküm yarıçapı 8-t şeklinde türetilmiş.

Delik konumları parametre kayıtlarında doğru:
- upperHoleY=B-G
- lowerHoleY=-G
- smallHoleX=-F
- E boşsa küçük delik yok; F=0 gerçek merkez konumu.

Bu ilişkilerle 92'nin üst Y=86,7 ve alt Y=-78,7 olur. Geçmişteki simetri hatası yok. 212'de +/-44,45 ve küçük delik X=-44,5; 200'de +/-44,5 ve üçüncü delik yok; 381'de +/-35 ve üçüncü delik merkezde. Bunlar parametre tarifinin sayısal değerlendirmesidir; işlem grafiği doğrulanmış/nativde çizilmiş anlamına gelmez.

İşlem sırası: dış silindir, iç boşluk silindiri, fark alma, iç/dış radyuslar, koşullu E deliği, C deliği, D deliği. Bu, eski tek pleyt kind'ı yerine genel işlemlerle kurulmuş bir açıklama.

## Yerel kontrolün reddettiği yer

holeC bir hole operasyonu, tek hedef gövde bekliyor. Ancak inputs=[outerFillet,holeE] verilmiş, holeE ayrıca optionalInputs içinde. E varken bu iki girdi aynı şey değildir: biri deliksiz gövde, diğeri E deliği açılmış gövde. E yokken ilk gövdeyle, E varken ikinci gövdeyle devam etme niyeti anlaşılabilir; fakat sözleşme böyle bir alternatif gövde seçimi tanımlamıyor. Doğru işlem zinciri seçimi veya açık koşullu seçim operatörü gerekir. Sadece girdi sayısı kontrolünü kaldırmak çözüm değildir.

Sonuç dört satırda RECIPE_VALIDATION / geçersiz işlem girdi sayısı: holeC. Program blocked-with-report ile durdu. Tarife elle fallback eklenmedi. Konum hatası değil, işlem bağımlılığı/koşullu gövde akışı hatası.

## Diğer inceleme noktaları

- outerFillet hedefi cup.outerRim diye yazılmış; R8'in alt büküm kenarına uygulanacağı semantik seçim native yürütücüde açıklaştırılmalı. Ağız kenarıyla karıştırılmamalı.
- Ağız kenarı yuvarlatmasını ölçüsüz olduğu için eklemediğini raporlamış; bu modelin varsayım kaydıdır.
- Ölçek/piksel oranı uyarısı verdi. Teknik resmin nominal boyutunu piksel oranıyla geçersiz saymak doğru değil; Excel'i değiştirme gereği bu uyarıdan çıkarılamaz.
- E sol tarafta doğru -F ile tarif edilmiş; modelin yansıma uyarısı konumun kesin yanlış olduğu anlamına gelmez.

## Kullanım

Input 15.542, completion 8.544 (3.830 reasoning dâhil), toplam 24.086 token. Sağlayıcı maliyeti 0,116524 USD. Cache okuma/yazma 0. Bir model çağrısı yapıldı; kaynaklar ve maliyet run-report/usage kayıtlarında. Kod veya prompt bu denemede değiştirilmedi.

Sonraki geliştirme: genel sözleşmede koşullu özelliğin gövde akışını tanımlamak (örneğin açık seçim ya da gövdeyi değiştirmeden geçiren no-op semantiği). Native geometri ve pafta yürütücüsü hâlâ tamamlanmadı. Bu görevde bu değişiklikler uygulanmadı.
