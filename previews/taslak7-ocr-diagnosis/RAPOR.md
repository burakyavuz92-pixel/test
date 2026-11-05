# Taslak7 OCR teşhisi

Üretim kodu, JPEG, Excel veya model yanıtı değiştirilmedi. Yeni API çağrısı yok. Bu klasördeki kırpımlar yalnız teşhis deneyidir; sonuç paftalarına elle etiket eklenmedi.

## F

Kaynakta [F] bir oval balonun içinde ve lider çizgisinin yanında. Mevcut OCR kayıtları aynı konumda FL, CIFL), IF], CIF] gibi metinler içeriyor. Kesin köşeli parantez filtresi bunları kabul etmiyor. Yalnız yazıyı içeren teşhis kırpımında Tesseract psm 7 ve 11 doğrudan [F] okudu. Çözünürlük yetersiz değil; çevre çizgilerinin metin alanına karışması ve mevcut sabit ROI sınırları sorunu gösteriliyor.

## 5

Gerçek [5] oval balon içinde. Kayıtlı OCR aynı yerde C151), (5), (1) üretiyor. Yalnız yazıyı içeren teşhis kırpımında psm 7 ve 11 [5] okudu. Eski detections.json içindeki 5 adayı ise G'nin bulunduğu farklı konumda; gerçek [5] ile uzaklık eşleşmesi başarısız. Bu yüzden paftaya alınmaması doğru.

## L

[L] eğik ve altındaki lider çizgisi paranteze çok yakın/bitişik. 315 derece taraması mevcut; açı hiç denenmemiş değil. Mevcut kayıtlar {u], {ul, Wu gibi okumalar veriyor. Teşhis kırpımını yataya çevirdiğimizde psm 11 {L] okuyor; açılış parantezi hâlâ yanlış. Diğer psm'ler tu gibi okumalar verdi. Basit yatay çizgi temizliği, 2x büyütme ve bilinear/bicubic döndürme bu örnekte tam [L] okumasını sağlamadı. Dolayısıyla L için yalnız büyütme/döndürme yeterli çözüm olarak gösterilemez. Karakter/parantez ayrımının güçlüğü ve çizgiyle yakınlığı birlikte değerlendirilmelidir.

L'nin model tarafından E olarak yorumlanması ayrıca model hatasıdır; OCR düzelmesi bunu kendiliğinden düzeltmez.

## Öneri

Balon dış çerçevesinden bağımsız, iç parantezli metin kutusunu ayıran genel ROI iyileştirmesi F ve 5 için bu deneyde destekleniyor. Eğik etiketlerde karakter/parantez ayrımı ayrıca sınanmalı. Kısa vadede taslak hazırlanırken metinle lider arasında boşluk bırakmak, gereksiz oval balonları kaldırmak ve mümkünse parantezli etiketleri yatay tutmak yararlı olur. (5) veya {L] gibi okumalar kanıtsız biçimde köşeli paranteze çevrilmedi.

## Token değerlendirmesi

6 satırlık taslak6.6 → 23 satırlık taslak7: toplam giriş 19.766 → 41.595 (+%110,4), görünen çıktı 5.131 → 7.510 (+%46,4), reasoning 37.709 → 54.104 (+%43,5). Farklı veri içerikleri de değiştiğinden bu karşılaştırma yalnız satır sayısının etkisini ölçmez.

Reasoning, 61.614 toplam çıktı tokenının %87,8'ini oluşturuyor. Çağrı başına en yüksek toplam çıktı 32.763; her çağrı için 65.536 bütçe ayrı uygulanıyor. API süreleri 130,4 ve 135,0 saniye; 600 saniye sınırının içinde. Ortak fonksiyon yaklaşımında bu örnekte reasoning satır sayısıyla doğrusal büyümedi. Bu gözlem 80 satır için kesin token tahmini değildir.
