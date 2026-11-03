# CadQuery akışı: taslak4.7'ye bağımlılık incelemesi

Bu inceleme mevcut çalışma ağacının statik incelemesidir. Yeni API çağrısı veya yeni taslakta uçtan uca doğrulama yapılmadı. Ürün numarası/ölçü harfine bağlı yerleşim kuralı bulunmaması, akışın genel olduğunu kanıtlamaz.

## Yüksek öncelikli bulgular

1. **Görünüş bölgeleri sabit.** `tools/inspect_template_dimensions.py:9` REGIONS ile kesiti solda, ana görünüşü ortada ve izometriyi sağ üstte varsayıyor. `inspect_bracket_layout.py` aynı bölgeleri kullanıyor. Başka yerleşimde etiket yanlış görünüşe bağlanabilir veya taranmaz. Çözüm: kaynak JPEG için görünüş bölgesi/oryantasyon keşfi; güvenilir değilse açık teşhis. Çıktı pafta düzeniyle girdi görünüş tespitini ayırın.

2. **Antet koordinatları belirli şablona ait.** `tools/fixed_template.py` REFERENCE, ERASE ve FIELDS alanlarını 7016×4961 referansına bağlıyor. Aynı en/boy oranındaki farklı antette yanlış yer silinebilir, ürün kodu yanlış hücreye yazılabilir. A5 çıktı ve seçilen antet bilinçli ürün tercihi olabilir; kaynak antetin aynı olduğunu en/boy oranı tek başına doğrulamaz. Şablon kimliği/config ve uygunluk kontrolü gerekir.

3. **Görünüş sınırı tespiti dar.** `tools/template_layout.py:source_frames` ana görünüşte tam çember, kesitte uzun dikey çizgiler arıyor. Yatay kesit, döndürülmüş resim, yarım görünüş, başka boyutta çizim veya konturu bölen çizgilerde çerçeve bulunamayabilir/yanlış bulunabilir. Çözüm: görünüşe göre oryantasyon ve kontur tespiti; çerçeve güveni ve başarısızlığı raporlanmalı.

4. **Tespit edilemeyen parantez sessizce kaybolabilir.** `template_layout.bind_dimensions` OCR eşleşmesi yoksa 'No bracketed template marker' ile omitted döndürüyor. Bu sonuç gerçek parantezsiz etiket ile OCR kaçırmasını ayırmıyor. Modelin tek başına yeni çizilebilir etiket eklemesi yasak kalmalı; ancak model/OCR envanter uyuşmazlığı ikinci yerel tespit veya açık eksik-ölçü teşhisi doğurmalı.

5. **Mevcut model kodu ve ölçü fonksiyonu parça ailesine özgü.** Deneme çıktısındaki T=3, H=33, radyuslar ve özel profil bu aile için üretilmiş veri; genel yürütücü kuralı değildir. Yeni JPEG için bunların yeniden üretilmesi gerekir. Başka aileye yalnız Excel değiştirerek uygulamak yanlış olur. Geometri, ölçü fonksiyonu ve görsel kanıtlar kaynak JPEG/kod hashleriyle birlikte tutulmalı; farklı kaynakla kullanım engellenmeli. Şu an parametre eşitliği kontrolü var; kaynak JPEG hash bağlaması bu pafta köprüsünde yok.

6. **Referans kapsamı belirli geometrilerde güçlü.** `tools/script_measurements.py` çap için silindirik yüz, radyus için daire/torus, eksen mesafesi için silindirik destekler kullanıyor. Konik yüz, spline geçiş, küresel radyus, kesik/bozulmuş yüz gibi durumlar aynı güvenle desteklenmiyor. Meridyen seçimi analitik yüz simetrisine dayanır; yerel kesme ile bozulan bölgede tekrar on-body kontrolü hata verebilir. Bu fiziksel imkânsızlık değil destek sınırıdır.

## Orta öncelikli bulgular

7. **Etiket tekilliği gereğinden katı.** `visual_measurements.merge` ve `template_layout.bind_dimensions` aynı kaynak etiketini birden fazla yerde görünce belirsizlik sayıyor. Yeni taslakta aynı ölçü ana görünüşte ve detayda tekrar edebilir. Tek anahtar yalnız harf/değer değil; görünüş + kaynak + ölçü ilişkisi olmalı.

8. **OCR piksel eşikleri çözünürlüğe bağlı.** `inspect_bracket_layout.py` çizgi temizliği ve karakter bölgelerinde sabit piksel boyutları kullanıyor. Görünüş bölgelerinin normalize olması bu sorunu gidermiyor. Farklı DPI/yazı boyutu testleri ve ölçek normalize etme gerekir. `read_columns` ölçülerin Excel'de F sütunundan itibaren olduğunu varsayıyor; kolonların taşınması yeni veriyi etkiler.

9. **Çıktı paftası sabit ve kapasitesi sınırlı.** `cad_recipe_executor.py` panel konumları, `drafting_style.py` A5 boyutu sabit. Bu 4.7 geometri ezberi değil; seçilmiş çıktı düzeni. Ancak çok derin/çok kademeli veya çok ölçülü yuvarlak parçada şeritler sayfaya sığmayabilir. Ölçü şeritleri başarısızlığı bildiriyor; görünüşleri/ölçeği otomatik yeniden paketleme henüz yok. Delik/radyus liderlerinde kesişim maliyeti küresel optimum değildir.

10. **Koordinat ve kesit kapsamı sınırlı.** Z ana eksen, üst yüz merkezi orijin, yerel V/H kesit ve tek izometri önayarı kabul ediliyor. Yuvarlak ailelerde bu ortak arayüz olabilir; bütün geometrinin dönel simetrik olduğunu kanıtlamaz. Eğik, birden fazla kesit, detay görünüşü veya ana ekseni başka yerde üretilmiş kod ayrıca ele alınmalı.

11. **Üretim komutu ile başarılı deney yolu farklı.** `src/CadScriptWorkflow.cs` mevcut Analyze metodu eski prompt/ortam model seçimini kullanıyor; ölçü fonksiyonu ve görsel işaret üretimini tek akışta istemiyor. Deneylerin Python çağrı yardımcılarıyla yapılmış olması, ana komutun aynı sonuçları otomatik üreteceğini göstermez. Tek bir sürümlü giriş akışı, kaynak bağlaması ve ara sonuç kontrolleri gerekli.

## Korunabilen genel parçalar

OCCT/CadQuery katı ve STEP işlemleri, kaynak toleransların korunması, parantez görünürlük ilkesi, ölçü değerinin geometriyle karşılaştırılması ve görünüş dışı ölçü şeritleri genel bileşenlerdir. Deneyde kullanılan nominal değerler, kaynak görüntü bölgeleri ve sabit antet hücreleriyle karıştırılmamalıdır.

## Önerilen sıra

1. Kaynak JPEG/kod/Excel bağlaması ve OCR envanter eksikliklerini sessizce geçmeme.
2. Görünüş tespiti ve antet şablonunu açık konfigürasyona ayırma.
3. Deneydeki başarılı aşamaları tek uygulama akışında birleştirme.
4. Farklı sayfa yerleşimi, DPI, tekrar etiket ve farklı yuvarlak geometri ailelerinde uçtan uca test.
5. Sonuçlara göre referans geometrisi ve pafta kapasitesini genişletme.

İnceleme sonuçları farklı taslakta doğrulama yerine geçmez. Bu raporda tespit edilen sınırlar henüz düzeltilmiş sayılmaz.
