# Yalnız veri sözleşmesi — verim incelemesi

Bu aşamada yalnız birim talimatı prompta eklendi. Yeni API çağrısı/çizim yapılmadı. High, tek JPEG/tek ayrıştırılmış tablo, açıklamasız başarı ve kısa hata yanıtı korunuyor. 55 yerel kontrol geçti; bu sonuç yeni promptun model üzerinde başarılı olduğunu kanıtlamaz.

## Uygulanan birim tanımı

Uzunluklar ve uzunluk payları mm, açılar deg, adetler count; yalnız oranlar/çarpanlar scalar. Türetilmiş hesaplar birimleri korur. İşlem alanlarındaki sabit sayılar alanın birimini alır: konum/uzunluk mm, açı deg, yön vektörleri boyutsuzdur. Sayısal alanları {value,unit} nesnelerine dönüştürmedik; mevcut sözleşmenin parametre birimleri ve tipli alanları korunuyor. Bu talimat önceki E+scalar2 hatasını hedefler; modelin buna uyacağı ancak sonraki çağrıda görülebilir. Birim doğrulaması gevşetilmedi.

## Somut gözlemler

Aktif prompt kaynak metni 6149 karakter; görev/girdi bölümü yaklaşık1358, sözleşme bölümü4791 karakter. Yaklaşık%78 sözleşme/arayüz tanımıdır. Bunlar token sayısı değildir. İşlem alanlarını rastgele kaldırmak modelin yazılım davranışını tahmin etmesine neden olabilir.

Son kapak veri-only yanıtının kopyasında yalnız yerel varsayılanlara eşit alanlar çıkarıldı: presence=always15, quantity=1 sekiz, visible=true dokuz, hideIf=never dokuz; toplam41 alan. Sıkıştırılmış JSON8066→7158 karakter, yaklaşık%11.3 azalma. Kaynak yanıt değiştirilmedi. Bu, token veya akıl yürütme azalması tahmini değildir. Bu dört varsayılan mevcut okuyucuda zaten destekleniyor; henüz başka alanın varsayılan desteği eklenmedi.

## Öneriler — henüz uygulanmadı

1. **Düşük etkili adım:** Dört mevcut varsayılan alanının yalnız farklı olduğunda gönderilmesi. Değer/özellik ilişkisi kaybetmez. projection gibi diğer alanları ancak okuyucuda varsayılanı tanımlandıktan sonra aynı kapsama almak gerekir.
2. **Yardımcı aritmetik:** İki kimlikli derived kaydı yerine güvenli, birimli sayısal sabitler içerebilen ifade ağacı. Örneğin parametre E ile {value:2,unit:mm} toplanabilir; çap {value:2,unit:scalar} ile bölünebilir. Serbest kod/formül çalıştırmak gerekmez. Ayrı two, topZ, t2 gibi yalnız bir kez kullanılan kimliklerin sayısını azaltabilir. Derleyici ve birim doğrulayıcı birlikte güncellenmeli; yeni çıktı sözleşmesi değişikliği, mevcut talimat revizyonundan daha geniştir.
3. **Tekrarlanan geometri:** Kapaktaki iki kanalın aynı doğru/yay profilini iki kez tarif etmesi yerine ortak profil ve dönüşüm referansı. Aynı şekli farklı konum/açıda kullanabilen genel bir işlemle uygulanabilir. Mevcut frame/operasyon anlamlarıyla native yürütücüye uyumu tanımlanmadan kısaltılmamalı.
4. **Ölçü hedefleri:** role alanları outerDiameter, face, thickness, pitchCircle gibi serbest metin. Daha kısa prompttan önce, bu hedeflerin gerçek OCCT yüz/kenar/eksene nasıl bağlanacağını kesinleştirmek değerli. Tanımlı seçiciler ve gerektiğinde yön/konum ile desteklenebilir. Tek bir face kelimesi birden fazla yüzü ayırt edemez. Bu, maliyetten çok doğruluk/verim sorunudur; modele daha fazla uyarı vermek çözüm değildir.
5. **Örnek satır seçimi:** Şu an büyük tablolarda blank/zero/value örüntüsü ham hücre metniyle seçiliyor. Ayrıştırılmış state/isZero üzerinden seçim 0, 0.0 ve benzeri eşdeğerleri tutarlı ele alır. Büyük veri setlerinin temsili için faydalı olabilir; bu aşamada örnek seçimi değiştirilmedi.
6. **Biçim doğruluğu:** response_format=json_object yalnız JSON ister; sözleşmeyi tam zorlamaz. Provider destekliyorsa yapısal şema kullanılabilir, fakat aynı şemayı promptta ikinci kez anlatmamak gerekir. Bu, semantik veya birim hatasını tek başına çözmez; bu incelemede servis yeteneği test edilmedi.

## Öncelik ve sınır

Önce mevcut varsayılanların tekrarını kaldırmak; ardından güvenli birimli ifade ağacı ve tekrar kullanılan geometri üzerinde çalışmak mantıklı. Genel native OCCT yürütücüsü tamamlanmadığı için sözleşmenin son verimini yalnız token üzerinden ölçemeyiz. Ölçü seçicileri ve işlem anlamları native katmana uygulanırken kayıp olmaması gerekir.

High düzeyi ve görüntü sayısı sabit tutularak aynı girdide işlenebilirlik, geometrik inceleme, görünür çıktı, akıl yürütme ve maliyet birlikte karşılaştırılmalı. Son veri-only denemesindeki düşüş olumlu bir gözlem; tek çağrı bütün değişkenleri ayıran deney değildir. Az token fakat yanlış/işlenemeyen tarif optimum sayılmaz. Burada önerilen adımlar için henüz yeni ücretli deney yapılmadı.
