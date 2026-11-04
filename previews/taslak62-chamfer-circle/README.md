# Pah ve dairesel kenar çapı desteği — Taslak6.2

Kayıtlı model geometri/ölçü referansları yeniden çizildi; yeni API çağrısı yapılmadı, STEP geometrisi değişmedi. Beş parçada 8/8 referans doğrulanıp yerleşti. 733001-03'te B, D ve sağ pah referansları geometriyle uyuşmadığından çözümsüz bırakıldı.

Pah desteği boy, açı, aynı konik/düzlemsel yüzey ve sınır uçlarını doğrular, tek oklu lider çizer. Konik pahın lideri kesitin gerçek meridyenine taşınarak yeniden yüzey üzerinde doğrulanır. Çap desteği silindir yanında tam dairesel kenarın merkez/eksen/yarıçapını doğrular; 25 koninin uç çemberinden bağlandı. Keyfî aynı değerde kenar seçilmez.

Bu doğrulama modelin seçtiği geometrinin var olduğunu kanıtlar; JPEG'deki okun doğru yorumlandığını tek başına kanıtlamaz. Özellikle kayıtlı sol pah referansı dış pahı tanımlar; taslaktaki iç ağız oku ile seçimin uyumu ayrıca gözden geçirilmelidir. Geçmiş geometri ve kamera korunmuştur; yeni +Z promptuyla yeniden geometri üretilmemiştir. Çıktılar inceleme amaçlıdır.
