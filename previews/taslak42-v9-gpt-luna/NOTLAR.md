# Taslak4.2 — GPT-6 Luna testi

Model openai/gpt-6-luna, high; tamamlanmış yanıt provider=OpenAI. Aynı orijinal taslak4.2.jpg, taslak4.xlsx, tam metin girdisi ve v9 sözleşmesi kullanıldı. Prompt ve geometri tarifi elle değiştirilmedi.

## Üç HTTP isteği ve taşıma uyarlaması

1. İlk istek HTTP 400 döndü; eski kod EnsureSuccessStatusCode çağrısını gövde okunmadan yaptığı için açıklama kayboldu. Bu rapor korunuyor.
2. Genel HTTP hata gövdesi kaydını ekleyip aynı isteği tanı amacıyla bir kez tekrarladık. Sunucu: görüntü 34320 patch gerektiriyor, sınır 30000. Yanıtta OpenAI ve fallback Azure aynı görüntü sınırı hatasını bildirmiş. Bu istek de model tarifi üretmedi.
3. Kaynak dosyayı koruyup yalnız API'ye gönderilen kopya 7016×4961 → 6400×4525 küçültüldü (32px hesabıyla 28400 patch). Kırpma, çizgi/ölçü silme veya ekleme yok. Modele bir JPEG ve bir ayrıştırılmış tablo gitti; orijinal ve küçük kopya birlikte gönderilmedi. Bu istekte tamamlanmış tarif alındı. Uyarlama sonraki Luna çağrılarında yazılım tarafından yapılır; geometriye özel değildir. Kare görseller için de patch sınırı uygulanır. `OPENROUTER_IMAGE_MAX_EDGE` ayarı kullanılabilir.

İlk iki 400 yanıtında usage alınmadı; sıfır maliyet ölçülmüş gibi gösterilmedi. Aşağıdaki ücret yalnız tamamlanmış isteğin bildirdiği tutardır. Otomatik geometri onarımı veya modelin hatalı tarifine tekrar çağrı yapılmadı.

## Kullanım

Input 37141; reasoning 16863; görünür completion 1023; toplam completion 17886; toplam token 55027. Bildirilen maliyet 0,01358555 USD. Yanıt dosyasına kadar yaklaşık 221 saniye (komut başlatma ve görüntü hazırlığı dahil; salt düşünme süresi değil). Cache read 0, cache write 37138 token. Ücret cache yazma dahil sağlayıcının bildirdiği tutardır; cache hit indirimi alınmış gibi sunulmadı.

Claude aynı orijinal veriyle 0,149180 USD, Nemotron 0,0139121 USD bildirmişti. Modellerin tokenizer ve görüntü işleme hesapları farklıdır; ayrıca Luna için taşınan JPEG küçültüldüğünden tüm girdiler byte düzeyinde aynı değildir. Bu karşılaştırma kalite üstünlüğü veya eşit reasoning bütçesi kanıtı değildir.

## Başarısız geometri yorumu

- Model kap gövdesini tanımamış: E kalınlıklı düz disk tarif etmiş. 33 mm derinlik, 3 mm cidar ve ilgili R8/R1,5 profilini oluşturmamış.
- Üç yuvarlak delik/şekillendirilmiş bölge yerine 120° polar desenle üç oval kanal üretmiş. D'yi kanal boyu, G/I'yi kanal genişliği, J'yi kanal çevresindeki yüzey boşaltması için kullanmış.
- F'yi dış disk kenar radyusu ve kanal çevresi boşaltma derinliği olarak yorumlamış. Kaynakta istenen yerel ağız biçimi yok. R2 ve J+6 uygulanmamış.
- Renk ve ölçü türleri de yanlış: A/C yeşil, B/I siyah gibi eşlemeler var.
- Yazılım ham tariften üç geçerli tek katı, STEP geri-okuma kontrolü ve üç JPEG önizleme üretti. Yanlış geometriyi yazılım düzeltmedi. Şeklin CAD açısından geçerli olması taslakla eşleşme değildir.
- Yerel antet/ölçü oku/eksen ve yerleşim sınırlamaları sürüyor; paket üretime uygun değil, hatayı incelemek içindir.

Bu örnekte GPT-6 Luna başarılı sayılmaz. Bütün GPT modellerine genellenmez. Geçerli görüntü gönderildiği ve gerçek sağlayıcıdan yanıt alındığı doğrulandı; modelin görseli içsel olarak nasıl yorumladığı ölçülemedi.

## Yazılım kontrolleri

91 mevcut C# kontrolü, derleme ve 3 yeni taşıma testi geçti. Yeni taşıma testleri kaynak dosyanın korunmasını/DPI/en-boy oranını, küçük görüntünün büyütülmemesini ve kare görselde patch sınırını kapsar. Geometri yürütücüsü ve sözleşme değiştirilmedi.
