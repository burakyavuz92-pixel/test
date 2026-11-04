# Parantez içeriği ve ölçü gösterimleri

Parantez tespiti artık yalnız harf/sayı listesiyle sınırlı değildir. Ham OCR metni saklanır; normalize içerik ayrı işlenir. Sabit boy, simetrik tolerans ve pah boyu/açı bilgisi `bracket_content.literal` tarafından ayrılır. Excel sunum sütunları ölçü kimliği değildir.

Her model işareti benzersiz `id`, her ölçü kaydı benzersiz `id` ve `markerId` taşır. `source` parantezde yazan metindir. Aynı metin tekrar edebilir. OCR adayları yakın konumla eşleştirilir; aynı OCR gösterimi iki kez tüketilemez. Ölçü bağlaması etiket yanında gösterim kimliğini de kontrol eder. Model işaretleri OCR tarafından bulunmayan parantezleri çizim için yetkilendirmez.

Taslak6.2 ham OCR çıktısında A, `[Al` olarak okunmuştur. Aynı konum başka dönüşte `[v]` olarak okunmuştur. Kapanış `l` normalizasyonu yalnız Excel'de tam eşleşen etiket için uygulanır; bilinen Excel etiketi farklı dönüşün yüksek güvenli bilinmeyen metniyle ezilmez. Bu normalizasyon bir OCR sezgisidir, genel bir karakter doğruluğu garantisi değildir.

OCR'nin `±` yerine `+` okuduğu durumda görüntüdeki iki yatay çizgi için konservatif piksel kontrolü uygulanır. Yalnız metne bakılarak `+` → `±` değişimi yapılmaz. Ham Tesseract TSV kayıtları açı/variant bazında saklanır. Üretim akışına ikinci OCR geçişi veya API ile etiket yetkilendirme eklenmedi.

Geometri yürütücüsü ayrıca yalnızca sonlu sayısal literal içeren büyük harfli modül sabitlerini kabul eder. Modül seviyesinde fonksiyon çağrıları veya geometri oluşturma hâlâ reddedilir. Bu değişiklik Taslak6.2 model yanıtındaki olağan sabit tanımlarını kabul etmek içindir; dönen geometri kodu elle değiştirilmemiştir.

Testler: `test_bracket_occurrences.py`, `test_bracket_layout.py`, `test_visual_measurements.py`, `test_cad_script_runner.py`, `test_cad_script_sheet.py`, `test_script_measurements.py`. İlk beş bağımsız test dosyası OCCT ortamında, yürütücü dosyası CadQuery ortamında çalışır.

Tam pafta başarısı bu testlerden çıkarılamaz: sabit görünüş bölgeleri E ve sağ pahı ön görünüşe atayabiliyor, yatay kesit için kaynak çerçeveleri bulunamayabiliyor. Bu örnekte API geometri kodu sabit tanım desteğinden sonra altı katı üretti, yüz etiketleri doğrulandı ve ikinci çağrı iki pah için ayrı referans verdi; pafta aşaması E görünüş uyuşmazlığında durdu. İlk otomatik akış raporu ile sonradan yapılan yerel devam testleri ayrı değerlendirilmelidir.

## Görünüş ataması revizyonu

OCR bölgesi yalnız ilk arama bilgisidir. Her model ölçü işareti gerçek geometriyi çevreleyen `viewFrameNormalized` kutusu ve ok konumlarıyla gelirse, görünüş bu geometrik referanstan alınır; ilk OCR bölgesi `ocrRegionView` içinde korunur. Kutu değerleri ve aynı görünüş içindeki tutarlılık doğrulanır. Kutunun doğruluğu model yorumudur; yalnız bu sayı kontrolleri görüntüsel doğruluğunu kanıtlamaz. STEP üzerinde ölçü bağlantısı ayrıca sınanır. Çerçeve/ok verisi olmadan çelişki sessizce geçilmez.

Yatay kesitlerde `sectionAxisNormalized`, +Z ekseninin kaynak görüntüdeki yönünü verir. Ölçü yönü kontrolü bu eksene dönüştürülür; sayfadaki yatay yön ile yazılımın çıktıdaki kesit yönü karıştırılmaz. Bu yön, çıktı paftasının yönünü değiştirmez.
