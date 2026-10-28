# Koşullu kesit denemesi

Kullanılan girdiler taslak2.xlsx ve taslak2guncel.jpg. Ortamda taslak.xlsx adlı dosya yok; bu JPEG'in önceki eşlikçisi taslak2.xlsx kullanıldı. Excel ve JPEG değiştirilmedi. Yazılım JPEG'i ve ayrıştırılmış dört Excel satırını API'ye gönderdi.

## Çıktılar

- [11-30-212.jpeg](11-30-212.jpeg): üç delik, kaçık üçüncü delik; kademeli kesit. Dört kapalı kesit bölgesi.
- [11-30-200.jpeg](11-30-200.jpeg): iki delik; düz kesit. Üç kapalı kesit bölgesi.
- [11-30-92.jpeg](11-30-92.jpeg): iki delik; düz kesit. Üst Y=86,7, alt Y=-78,7; simetriye zorlanmadı.
- [11-30-381.jpeg](11-30-381.jpeg): üç delik, üçüncü delik merkezde; düz kesit. Sıfır F ölçüsü gizlendi, delik korundu.

Dört çıktı da insan kontrolü bekliyor; üretim onayı değildir. 1754×1240 piksel, kaynakla aynı 300 DPI. Nominal ölçüler geometri, toleranslar gösterim verisidir. Arial kullanıldı; yeşil sabitler geometride kullanılıp gösterilmedi.

## Akış ve insan müdahaleleri

İlk geliştirme çağrısında model yanlış F/G bağlantıları kurdu; yerel denetim çizimi durdurdu. Yazılıma en fazla bir otomatik yeniden değerlendirme eklendi. İkinci çalışmanın ilk yanıtı simetri ve kesit hedefleri konusunda hatalıydı; kodun ürettiği hata raporu ile otomatik ikinci yanıt alındı. Son yanıtta B-G/-G/-F ve üç hedefli kesit doğru döndü. Asistan modelin formüllerini veya Excel değerlerini elle değiştirmedi, kullanıcıya soru yöneltilmedi.

Kamera modelden negatif Z ile geldi; mevcut kapalı-yüz kontrolü çalışmayı durdurdu. Bu ailede ön yüz +Z olduğundan kamera Z bileşenini ön tarafa yansıtan açık yerel sunum politikası eklendi. Kaynak kamera model-plan.json içinde değişmeden durur, çözülmüş kamerada frontFacePolicyAdjusted kaydı bulunur. Bu otomatik açı düzeltmesi referansla birebir açı eşleşmesi garantisi değildir.

Kayıtlı yanıt kaynak SHA256 kontrolüyle yeni API çağrısı olmadan yürütüldü. Asistan görsel incelemede merkez/yan delik liderlerinin üst delik etiketiyle çakışmasını gördü; genel merkez-seviyesi lider yerleşimini sola taşıdı ve yerelde yeniden çizdi. Ayrıca kademe geçişi delik kenarları arasındaki güvenli boşluğun ortasından seçildi. Bu nedenle geliştirme sırasında hiç asistan müdahalesi olmadığını iddia etmiyoruz. Bundan sonraki aynı akış bu kuralları yazılım içinde uygular.

## Doğrulama ve maliyet

49 C# kontrolü, 9 OCCT geometri/kesit kontrolü geçti. Yerel OCCT çıktıları BRep, tek katı, delik hacmi ve STEP tekrar-okuma doğrulamalarından geçti. Kademeli kesitte yapay yatay geçiş kenarı oluşmaması test edildi.

Bu görevde toplam 3 API çağrısı: ilk çalışma 0,034028 USD; otomatik değerlendirmeli çalışma iki çağrıda 0,080046 USD; toplam 0,114074 USD. Yerel yeniden çizimlerde API çağrısı yok. API yanıtı öncesi yazılım geliştirilmiş olduğundan bu maliyet tek bir normal çalışmanın kesin ücreti değildir.

## Sınırlar ve sonraki adım

Kesit desteği, ana düzlemde başlayıp biten paralel kesit bantlarıyla sınırlı. Hedef deliklerin Y aralıkları arasında geçiş boşluğu olmalı. Genel eğik/döndürülmüş kesit veya kaynaklı montaj desteği yok. Kesit arkasındaki çeper kenarları ana düzlem HLR hesabından gelir; genel kademeli arka-kenar görünürlüğü henüz çözülmedi. Pafta yerleşimi hâlâ bu yüksek çözünürlüklü şablona kalibre. Kamera politikası ve lider seçimi yaklaşıktır; genel yazı çakışma çözümü yok. Bazı ölçüler kağıtta küçük görünebilir; teknik kullanım öncesi kontrol edin.

Bir sonraki adım, dört JPEG'in kesit boşlukları, görünür kenarları, izometrik yönü ve ölçü yerleşimini birlikte değerlendirmek. Bunlar kabul edilmeden büyük veri setine geçilmemeli. Modelin gelecekteki her yeni grubu doğru okuyacağı garanti edilmez; iki denemede çözülemeyen plan raporla durur.
