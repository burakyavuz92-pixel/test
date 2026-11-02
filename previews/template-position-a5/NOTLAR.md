# Taslak konumunu önceleyen ölçü yerleşimi

API çağrısı yapılmadan aynı altı satır ve önceki kayıtlı tarif yeniden işlendi. Geometri değiştirilmedi. Önceki çevrimdışı testin I→L referans uyarlaması korunmuştur.

Taslağa bağlı üretim yolunda, metin oklar arasına sığmıyorsa otomatik dışarı taşıma kuralı kaldırıldı. İlk aday artık taslaktan aktarılan metin merkezidir. Çakışma denetimi korunur. Sabit 13 piksel merkez–çizgi uzaklığı yerine gerçek yazı yüksekliğinin yarısı + 2 çıktı pikseli kullanılır; dikey metinde de aynı ölçü döndürülmüş yazıya uygulanır. Dar collider ve üst üste asimetrik tolerans yazımı korunmuştur.

11-24-13 J/20,5: önceki konum (237,17;548,40), yeni konum (201,17;468,09). Taslak hedefi (249,17;468,09). Otomatik aşağı atma kalktı; geometri/etiket çakışma araması 48 piksel sola kaydırdı. Bu kayma kaldırılmış değildir. D ölçüsü de artık zorunlu dışarı taşınmaz. Kesitte ölçü çizgileri ve komşu metinler hâlâ sıkışabilir; tüm çizgi kesişmeleri bu çalışma kapsamında çözülmedi.

Dört satırda 11, B=0 olan iki satırda 10 ölçü yerleştirildi; çözülemeyen bağlantı yok. Bu kayıtlar görsel uygunluk onayı anlamına gelmez. Her satırın placement.json dosyası hedef ve gerçekleşen merkezleri içerir.

Doğrulama: kısa ölçü aralığında uzun yazının taslak merkezinde tutulması ve çizgi mesafesinin yazı kenarına yaklaşması için regresyon testi eklendi. İlgili 23 test geçti.
