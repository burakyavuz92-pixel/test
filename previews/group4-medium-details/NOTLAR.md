# Taslak4 — medium ve detay görünüşü

Kullanıcının isteği: detay görünüşünü mevcut geometri/görünüşe bağlı veri olarak ekle, medium kullan, aynı taslak4'ü tekrar gönder, girdileri değiştirme.

JPEG ve Excel dosyaları önceki high çağrısıyla SHA256 olarak birebir aynı; source-comparison.json bunu gösterir. Yerel ayrıştırılmış tabloyu veya çizimi elle değiştirmedik. Prompt yalnız genel detay görünüşü alanıyla genişletildi; F'nin içeri çökme yönü hakkında talimat/ek yorum eklenmedi. Görev metni, geometri sözlüğü ve diğer talimatlar korundu. Medium tek çağrı, yeni değerlendirme döngüsü yok.

## Uygulanan destek

Model detay için `{id,label,sourceView,features,sheetBox}` veriyor. Yazılım mevcut katının kaynak görünüşünü/kesitini ilgili özelliklerin sınırlarıyla kırpıp büyütüyor. sheetBox normalize sayfa kutusu, yeni detay geometrisi yok. Başlıca oluşturma özelliği seçilmişse modifier/hole referansının bütün gövde sınırlarını detay odağına taşıması önleniyor. Kutunun sayfa içinde olması, bilinen geometri/görünüş referansları kontrol ediliyor. Ayrı sentetik test geometrisinde JPEG içinde detay üretimi sınandı; bu test kullanıcı girdisi veya yeni API yanıtı üzerinde düzeltme değildir.

74 C# kontrolü,8 native test geçti. Native testler kırpma çizgilerini, odak sınırını ve mevcut katıdan detay JPEG'i üretmeyi kapsıyor. Bu testlerin geçmesi modelin yeni parça tarifinin doğru olduğunu kanıtlamaz.

## Gelen veri

Model Detay B döndürdü: kaynak sectionView; özellikler boss ve centerHole; sheetBox=[0.30,0.64,0.12,0.16]. Bu alan sözleşmeye uyuyor ve taslaktaki alt-sol detay bölgesine karşılık geliyor.

Ancak geometri önemli hatalar içeriyor:

- holeG ve holeI aynı y=C/2 konumunda. Alt delik yok; ikinci işlem aynı çapta aynı deliği yeniden açmaya çalışıyor.
- İç çap A−wall (wall3) verilmiş; dış/iç çap farkı3 olduğundan radyal duvar1.5 oluyor. Beklenen3 değil.
- İç kesici z−3'ten30'a uzanıyor; gövde33 yüksekliğinde, kalan kapalı yüz yanlış uçta.
- boss x=+B; front kamera+Z olduğundan taslaktaki sol konumun tersinde. E kadar uzunluk verilmiş, F geometride hiç kullanılmamış. 0.5 içe çökme bu yanıtta çözülmedi.
- R8/R1.5/R2 detayları bu tarifte modellenmemiş. F yalnız parametre listesine konmuş; ölçülendirme kaydı da yok. Yerel ilk doğrulayıcı parametrenin listede varlığını kontrol ediyor, bütün belirtilmiş ilişkilerin kullanıldığını/geometrik doğruluğu kanıtlamıyor.

Ham recipe.json elle değiştirilmedi. Yürütücüye verildiğinde üç üründe de `Hole does not remove material: holeI` hatasıyla durdu. Yeni JPEG0. Mevcut kontrol gevşetilmedi; önceki high görsellerinin üzerine yazılmadı. Yeni detay görünüşü bu API yanıtından çizdirilemedi; geometri daha önce durdu. Doğruymuş gibi bir görsel yayımlanmadı.

## Maliyet

|Metrik|Önceki high|Bu çağrı medium isteği|
|---|---:|---:|
|Giriş|9213|9372|
|Akıl yürütme (bildirilen)|9858|0|
|Görünür çıktı|4163|2144|
|Toplam çıktı|14021|2144|
|Maliyet USD|0.158636|0.040184|

Cache0. İstek gerçekten effort=medium; run-report bunu kaydediyor. Sağlayıcı reasoning_tokens0 bildirdi, bunu medium'un ne kadar iç hesap yaptığına dair bağımsız kanıt sayamayız. Medium ayarı ve detay sözleşmesi birlikte değişti; bu bir tek-değişken deneyi değil. Fiyat yaklaşık%75 düştü, fakat yeni tarif kullanılamadı. Dolayısıyla maliyet hedefi doğrulukla birlikte sağlanmadı. Özel akıl yürütme metni yayımlanmadı.

## Son durum

Detay alanları ve yerel çizim desteği kaydedildi; varsayılan akıl yürütme kullanıcı isteğiyle medium. Kullanıcı kaynakları ve API yanıtları değiştirilmedi. Sonraki adım için otomatik bir çağrı veya geometri tamiri yapılmadı. Bu deneyden üretim onaylı tarif oluşturulmadı.
