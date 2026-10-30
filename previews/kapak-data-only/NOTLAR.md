# Kapak — yalnız veri promptu

Tek kapaktaslak.jpg + kapaktaslak.xlsx yazılıma verildi. Yazılım tek orijinal JPEG ve ayrıştırılmış tabloyla OpenRouter'a tek çağrı yaptı. Model ve high akıl yürütme ayarı korundu; otomatik tekrar çağrı yok. JPEG/STEP üretilmedi; modelin tarifi elle düzeltilmedi.

## Değişiklik

Prompt görev metni yeniden yazıldı. Başarı yanıtı yalnız schemaVersion/geometry/drawing; hata yanıtı yalnız kısa Türkçe error cümlesi. description/evidence/precision/issues alanları artık istenmiyor. Sabitler için estimated şartı okuyucudan kaldırıldı; eski v7 kayıtları okunabilir. Açıklamaların ve varsayımların yazılması istenmiyor. Belirtilen ölçüler uygulanıyor, eksik geometrik detaylar taslakla tutarlı tamamlanabiliyor. Boş ve sıfır ayrıştırılmış girdide korunuyor; sütuna özel sıfır senaryoları anlatılmıyor. İşlem anlamları, koordinat/ölçü bağlantıları korunuyor. Başarı yanıtı işlenebilirlik anlamındadır, geometrik doğruluk garantisi değildir.

47 kontrol geçti; derleme hatasız. Testler veri-only başarıyı, kısa hata yanıtını, yerel ölçü varsayılanlarını, tolerans ayrımını ve önceki bağımlılık kontrollerini kapsıyor.

## Token ve maliyet

Karşılaştırma aynı kapak veri setinin bir önceki tamamlanan v7 çağrısıyladır; önceki kesilen ilk çağrı buraya dahil değildir.

| Metrik | Önceki | Yalnız veri |
|---|---:|---:|
|Giriş|8836|8540|
|Akıl yürütme|16165|6623|
|Görünür çıktı|8661|4137|
|Toplam çıktı|24826|10760|
|Maliyet USD|0.265932|0.124680|
|Cache token|0|0|

Akıl yürütme yaklaşık %59, görünür çıktı %52, toplam çıktı %57, maliyet %53 azaldı. Tek deneme nedensel kanıt değildir; modelin seçtiği tarif de değişti. Azalma cache indiriminden kaynaklanmıyor. Ham özel akıl yürütme yayımlanmadı.

## Gelen tarif

- Beklenen dış çap A, hatve çapı B, dört delik C, merkez deliği D, çıkıntı yüksekliği E ve sac kalınlığı F kaynakları korunmuş.
- Çıkıntı dış çapı bu kez22 mm seçilmiş (önceki20); artık etiket/açıklama yok. Kullanıcının tercih ettiği davranış bu: seçimin kaynağı çıktıdan ayırt edilemez.
- İki kenar kanalı 45/225° bazlarında, doğru/yay segmentlerinden kapalı profil olarak tarif edilmiş. Genişlik14, radyus7, iç uç A/2−16.5. Yeni tarife geçilince geometri kökeni z=0 ön yüz, sac −Z, çıkıntılar +Z olarak seçilmiş; önceki orijinden farklı olması tek başına hata değil.
- Tüm özellikler always; E=0 için ek bir senaryo/uyarı üretilmemiş. Yanıtta açıklama/rapor/tahmin etiketi yok.
- Siyah ölçüler kaynak sütunlara bağlı, yeşil ölçüler renk bilgisiyle verilmiş. Yerel katman yeşili gizler; model visible=true yazsa da yerel kural geçerlidir.

## İki somut hata

1. **Birim uyuşmazlığı — yazılım yakaladı.** `two` unit=scalar iken `topZ=E+two`, `toolLen=t2+two`, `fPlus2=F+two` türetilmiş. Burada 2 mm kesici payı ile boyutsuz iki çarpanı aynı parametreye yüklenmiş. Birim doğrulaması bu nedenle üç satırı da durdurdu. Kontrol gevşetilmedi, ham tarif değiştirilmedi. Bu hata parça ölçüsünü anlamaktan ziyade kesici yardımcı hesaplarını sözleşmede ifade etme sırasında oluşmuş.

2. **Kesit yönü — incelemede görüldü.** Dünya bazında yol [0,−150,0]→[0,150,0] (Y doğrultusu), extrusionDirection=[1,0,0] verilmiş. Bu yol X boyunca süpürülünce XY düzlemi z=0 oluşur. İstenen merkezden geçen düşey kesit için iz Y boyunca, süpürme Z boyunca olmalıydı. Bölüm görünüş yönü ise X. Model kesme yüzeyinin süpürme yönüyle bakış yönünü karıştırmış görünüyor. Bu ikinci bulgu mevcut doğrulayıcının otomatik geometrik kanıtı değildir; tarif incelemesidir.

Sonuç: veri-only çıktı ve maliyet açısından hedefe yaklaşıldı; ancak tarif çalıştırılabilir olarak onaylanmadı (`blocked-with-report`). Sonraki geliştirmede kesici payı gibi yardımcı hesapları yerelde üretmek ve kesit düzlemini normal/iz üzerinden daha doğrudan tarif etmek değerlendirilebilir. Bu denemede bunlar değiştirilmedi ve yeni ücretli çağrı yapılmadı. Genel native OCCT yürütücüsü hâlâ tamamlanmadı.
