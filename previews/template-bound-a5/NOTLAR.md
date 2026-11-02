# Taslağa bağlı yerel ölçü yerleşimi

API çağrısı yapılmadan altı satır render edildi. Bu bir yeni model denemesi değildir: kayıtlı Haiku geometri tarifindeki eski Excel I referansları güncel L sütununa taşındı; geometri düzeltilmedi. Güncel taslak4.6 Excel ve taslak4.5 ile byte olarak aynı JPEG kullanıldı. Önceden bu JPEG üzerinde çalıştırılmış OCR kayıtları kaynak SHA256 ve sütun düzeni eşleşmesiyle yeniden kullanıldı. Üretim yolu önbellek yoksa OCR'ı kendisi çalıştırır.

Excel sütunlu ölçüler etiket adına; sabit ölçüler eşleşen [3], [R2] gibi literal etikete bağlanır. Köşeli parantezsiz ölçüler yerel yerleşime alınmaz. Kaynak görünüş ve parçaya göre göreli konum aktarılır; uzun metin için aynı görünüşte yakın adaylar denenir. Ok uçları desteklenen gerçek OCCT geometrisinden çözülür. Diş metinleri yerel Excel ayrıştırıcısından gelir.

Dört satırda 11, B=0 olan iki satırda 10 ölçü yerleştirildi; çözülemeyen bağlantı kaydı yok. Bu sayı görsel kusursuzluk anlamına gelmez. R2'nin eski geometri hatası korunmuştur. Bazı uzatma çizgileri ve komşu ölçüler birbirine yaklaşabilir; tüm çizgi-çizgi kesişmelerini çözen yönlendirme yoktur.

Sınırlar: mevcut sabit pafta düzenindeki yuvarlak ana görünüş ve dik kesit konturu tespiti desteklenir. Keyfi yeni pafta/görünüş otomatik tanıma tamamlanmış değildir. OCR dönüş açısı gerçek yazı açısını her zaman vermez; özellikle L'nin açısı birebir kopyalanmış sayılmaz. Radyus tarafı seçimi kaynak yazı doğrultusundan yaklaşık çıkarılır, gerçek ok ucu OCR ile tespit edilmiş değildir. Bir etiket bulunamazsa raporda atlanan ölçü olarak görünür; yazılım bunun kullanıcı tercihi mi OCR kaçırması mı olduğunu bilemez. Belirsiz çoklu etiket ve eksik görünüş konturu hata kaydına alınır.

Her çıktının dimension-placement.json dosyası bağlanan etiket, görünüş, istenen ve gerçekleşen metin konumunu kaydeder. JPEG/PDF dosyaları insan kontrolü için inceleme çıktılarıdır.
