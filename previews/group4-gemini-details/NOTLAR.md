# Aynı taslak4 testi — google/gemini-4-argon

Çalışan OPENROUTER_MODEL google/gemini-4-argon; API yanıtının model alanı da aynı. Önceki medium+detay testindeki JPEG, Excel ve prompt/tablo metniyle birebir aynı girişler kullanıldı. SHA256 karşılaştırması comparison.json içinde. Kaynak geometri yönü/F0.5 hakkında ek açıklama gönderilmedi. Kod ve prompt bu denemede değiştirilmedi. Tek yeni API çağrısı; medium isteği ve32768 çıktı sınırı korundu. Model yanıtı elle değiştirilmedi, kontrol gevşetilmedi, tekrar çağrı yapılmadı.

## Gelen tarif

- G/I delikleri bu kez y=±C/2, birbirinden ayrı. B0 merkezdeki manşon/delik korunuyor.
- Sacın silindirik yan duvar nominali3; kapalı ön yüz3. R8 veR1.5 parametre olarak ve ölçü tanımında yer alıyor, fakat cup_sketch kapalı çokgen. Köşe geçişi yay değil düz çizgi; R1.5 dudak geometrisi uygulanmamış. Parametre/ölçü tanımlamak ilgili geometrinin gerçekten üretildiğini kanıtlamıyor.
- Manşon z=−F'ten E−F'e uzanıyor. Kullanıcının belirttiği içe0.5 çökertme yerine hâlâ dışa0.5 taşma var. Bu yönde düzeltme eklenmedi.
- Ön görünüş kamera−Z; manşon dünya x=−B. Bu kamerada ekran sağ−X olduğundan manşon taslaktaki sol yerine sağa düşebilir. Kameraya dokunulmadı.
- Detay B kaydı var: section_AA kaynağı, boss_Outer_cyl/boss_bore/final_body özellikleri, normalize kutu[0.28,0.61,0.14,0.26].
- B yeşil olmasına rağmen dim_B sourceColor atlanmış; yerel black varsayılanıyla B ölçüsü gizlenmez (B0 ise hideIf ile gizlenir). Görselden renk okuma doğru yapılmamış.

## Yerel yürütme

İlk C# sözleşme/parametre/kesit doğrulaması üç satırı çözümlüyor. Native OCCT yürütücüsü üç satırda `No edge matches geometric selector final_body` hatasıyla duruyor. Üretilmiş JPEG0.

R2 seçicisinde near, manşonun taban çemberinde, direction=[0,0,1]. Mevcut yürütücü bu alanı kenar teğeti olarak denetliyor; çember teğeti bu noktada Z değil. Promptta direction için "axis/tangent as appropriate" ifadesi bulunduğundan alanın çember ekseni mi teğeti mi olduğu yeterince kesin değil. Bu durumu yalnız model hatası diye değerlendirmemeliyiz: arayüz anlamının da netleşmesi gerekiyor. Bu denemede mevcut kontrol modele göre değiştirilmedi. Seçici sorunu giderilse bile R8/R1.5 geometrisi ve F yönü yanlışları ayrıca mevcut.

Önceki görsellerin üzerine yazılmadı. Geçmeyen tarifi doğru göstermek için elle onarma veya görüntü üretimi yapılmadı. Native durma nedeni native-results.json içinde.

## Maliyet

|Metrik|Sonnet medium isteği|Gemini medium isteği|
|---|---:|---:|
|Giriş token|9372|3936|
|Bildirilmiş akıl yürütme|0|0|
|Görünür/toplam çıktı|2144|2406|
|Maliyet USD|0.040184|0.031932|

Gemini çağrısı yaklaşık%21 daha ucuz; önceki Sonnet high taslak4 çağrısı0.158636 USD idi. Cache0. Aynı prompt/JPEG farklı modellerde farklı token sayılır; giriş tokenının düşmesi daha az veri gönderdiğimiz anlamına gelmiyor. Medium istendiği hâlde sağlayıcı reasoning_tokens0 bildirmiş; bunu iç hesaplamanın hiç yapılmadığı şeklinde yorumlayamayız. Ham özel akıl yürütme yayımlanmadı.

Sonuç: model değişimi için geometri kodu değiştirmek gerekmedi, fakat bu tarif henüz kullanılabilir sonuç vermedi. Bu denemeden üretim onaylı tarif oluşturulmadı.
