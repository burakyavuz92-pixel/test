# Taslak4.4 — köşeli parantezli konum tespiti

Yeni taslak4.4.jpg ve taslak4.4.xlsx ile yerel OCR test edildi. AI/API çağrısı yapılmadı; CAD veya ürün çizimi üretilmedi. Orijinal etiket konumlarına manuel ekleme yapılmadı. Önizleme kaynak taslak üzerindeki tespit kutularıdır.

## Sonuç

Excel'in ilk beş ayar sütunu dışındaki 10 etiketten 9'u bulundu: A, B, C, D, E, F, G, J, K. I bulunamadı. Ayrıca [3] ve [R2] tespit edildi: toplam 11 kabul edilmiş aday. Parantezsiz R5, R8, R1,5 ölçüleri yerleşim etiketi yapılmadı. Bu dışlama geometrinin bu verileri kullanamayacağı anlamına gelmez; API aşaması bu testte çalıştırılmadı.

Kesit: A/D/E/F/J/K, 3 ve R2. Ana görünüş: B/C/G. Okuma yönleri yatay, dikey, G için yaklaşık 30 derece ve R2 için yaklaşık 45 derece. I bu taslakta yaklaşık 15 derece eğimli; eğiklikten bağımsız olarak ØI bileşiği tekil OCR'de de güvenilir okunamadı. Dolayısıyla yatay yazma zorunluluğu koyulmadı; ancak bütün etiketler ve her keyfi açıda başarı garanti edilmiyor.

## Nasıl çalışır?

Görünüş bölgeleri bu sabit pafta düzenine göre kalibre edilir. 15 derecelik aralıklarla bütün yönler taranır. Uzun çizgileri ayıklanmış ve orijinal görüntü birlikte okunur. Bazı açılarda yerel yazı bölgeleri ayrıca OCR'ye verilir. Yazılar önceden yataya çevrilmek zorunda değildir; dönüşüm yazılımda yapılır, bulunan kutu/poligon kaynak koordinatlarına geri taşınır. Konumlar normalize olarak da saklanır. Ok/uzatma çizgisi geometrik bağlantıları henüz çıkarılmadı.

Sadece hem açılan hem kapanan köşeli parantezi okunan ifadeler aday olur. Çap işareti bazen D/P gibi okunur. Excel sütunu çap içeriyorsa ve ham etiket tam bir sütun adı değilse, yalnız bu açık bağlamda simge-harf ayrımı yapılır; DA→A, PD→D, DJ→J, DK→K gibi düzeltmeler JSON normalization alanında kaydedilir. Var olan gerçek DA sütunu varsa A'ya çevrilmez. F için 180 derece okumada çıkan 4 gibi aynı konumdaki daha düşük güvenli okumalar elenir. Eşleşmeyen RQ yanlış okuması rejectedCandidates listesine konur, önizlemede kabul edilmiş gibi gösterilmez. Böylece eksik parantez tahminle eklenmez.

OCR güven puanı doğruluk garantisi değildir; bütün kayıtlar needs-review durumundadır. Son kutular görsel incelendi. Yeni [A] biçimi için eski tek tırnaklı araç ayrı tutuldu. Model promptu köşeli parantezleri ve eski tırnakları tanımlayacak şekilde güncellendi, fakat bunun için API çağrısı yapılmadı.

## Sınırlar ve sonraki adım

Bu sonuç otomatik üretim yerleşimine bağlanmadı. I eksik olduğundan yerleşim profili tam değildir; konumu uydurulmadı. Kullanıcı [ØI] yerine [I] veya Ø[I] kullanırsa parantez içindeki sınıflandırma sadeleşir; bunun yeni bir gerçek taslakla ölçülmesi gerekir. Parantez dışındaki Ø işaretini okuma zorunluluğu yoktur; çap bilgisi Excel'de kalır.

Konum bulmak yalnız bir aşamadır: bulunan ölçü görünüşünün korunması, ok ucu ve uzatma çizgisi yönünün çözümlenmesi, farklı boyutta yeni parçaya aynı düzenin aktarılması sonraki işlerdir. Mevcut sabit-koordinatlı ölçülendirme üreticisi bu test sonuçlarıyla değiştirilmedi. Görünürlük Excel düzenine girilmedi.

## Tekrar çalıştırma

`python tools/inspect_bracket_layout.py samples/taslak44-upload/taslak4.4.jpg output/new-bracket-test --excel samples/taslak44-upload/taslak4.4.xlsx`

Tesseract CLI, Pillow, NumPy ve OpenCV gerekir (tools/requirements-template-ocr.txt). OCR CPU üzerinde çalışır; API anahtarı gerekmez. Yerel işlem süresi bölge sayısına göre birkaç dakika olabilir. 4 birim testi köşeli parantez zorunluluğu, çap-normalizasyonu ve döndürülmüş koordinat dönüşümünü kontrol eder. Bu testler eksik I'nin tespit edildiği iddiasını taşımaz.
