# Yeni ilişki şeması ve tek çağrılı deneme

Girdiler kullanıcının yeni taslak2guncel.xlsx dosyası ve mevcut taslak2guncel.jpg. Kaynak SHA256 özetleri original-run-report.json içinde. Dosyalar değiştirilmedi. Yazılım JPEG'i ve dört ayrıştırılmış Excel satırını API'ye gönderdi. Tek çağrı, 0,032152 USD. Otomatik yeniden değerlendirme veya ikinci API çağrısı yapılmadı.

## Yazılım değişiklikleri

Geometri artık ayrı ilişkilerle tanımlanıyor: her koordinat ana eksene ya da başka bir özelliğin koordinatına göre ölçü sütunu ve yön içeriyor. Cebirsel formülü yazılım hesaplıyor. Ölçülerin görünürlüğü ayrı annotations bölümünde; örneğin herhangi bir sütunun başka sütunun yarısına eşit olması yalnızca gösterimi etkiliyor. Çözücüde B/G sütunlarına özel geometri kuralı yok. Kamera modelin verdiği yönde kaldı, işaret yansıtması yok.

Kesit amacı ve hedef özellikleri modelden gelir. Olmayan hedefler satırda çıkarılır; aynı düzlemdeki kademeler birleşir. Kesit etiketinin plandan gelmesi desteklendi. Motor hâlâ yalnızca Y boyunca paralel bantları, merkez düzlemindeki uçları ve delikler arasında güvenli geçişi destekler. Eğik/döndürülmüş kesit, kaynaklı montaj veya genel parça desteği eklenmedi.

212'de önceki delik üst/alt çizgisi eksikliği için her bantta ayrı görünürlük hesabı yapıldı. Gerçek delik kenarları korunur, yapay bant sınırları elenir. Buna regresyon testi eklendi.

## Modelin ilk ve tek yanıtı

Model F'yi üst/alt deliklerin X konumuna bağladı, G'yi koordinat hesabında kullanmadı. Boş F bulunan satırlar çözülemedi; G ölçüsü nominal geometriyle uyuşmadı. Ayrıca kesitte E deliğini dışarıda bıraktı ve yeşil sabitleri görünür işaretledi. İlk iki sorun yerel doğrulamada yakalandı. Kesit hedefi ve yeşil gösterim yanlışlığı bağımsız görsel denetimde fark edildi; şu an yazılım bunları tek başına kesin olarak yakalayamıyor.

**Sonuç: Yeni şema modelin yanlış görsel eşlemesini tek başına çözmedi. Bu çizimler özerk başarı örneği değildir.** Normal program bu planı raporla durdurur.

## Bu denemeye özel asistan müdahalesi

Kullanıcının açık izniyle, original-model-plan.json korunarak assisted-plan.json hazırlandı:

- Üst deliğin X konumu 0, Y konumu alt delik Y+B yapıldı.
- Alt deliğin X konumu 0, Y konumu -G yapıldı.
- F ölçüsünün hedefi E deliğine taşındı. E deliğinin X=-F/Y=0 tanımı zaten doğruydu, korundu.
- Yeşil R8, 33, 3 gösterimleri gizlendi; geometride korundu.
- Kesit hedeflerine E deliği eklendi.
- Kamera aynen modelin seçtiği (-0,6;0,5;1) olarak korundu. Excel değerleri/toleransları değiştirilmedi.

Assisted plan ile ilk yerel çizim girişiminde, olmayan isteğe bağlı kesit hedeflerinin eski adaptöre aktarılmasında yazılım hatası bulundu. Hedefler aktif özelliklere göre filtrelenecek şekilde kod düzeltildi, buna test eklendi. Aynı plan yeni API çağrısı yapılmadan başarıyla çizildi. render-report.json AssistantAnswersUsed=true içerir.

## Çıktılar

- [11-30-212](11-30-212.jpeg): üç delik, kademeli kesit; delik üst/alt görünür kenarları eklendi.
- [11-30-200](11-30-200.jpeg): iki delik, düz kesit.
- [11-30-92](11-30-92.jpeg): iki delik, asimetrik Y konumları, G ölçüsü gösteriliyor.
- [11-30-381](11-30-381.jpeg): merkezde üçüncü delik, düz kesit; F=0 ve G=B/2 ölçüleri gizli.

1754×1240, 300 DPI, Arial. Aynı nominal katıdan bütün görünüşler üretildi. 59 C# kontrolü ve 10 OCCT kontrolü geçti; dört katı BRep/tek katı/delik hacmi/STEP yeniden-okuma denetimlerinden geçti. Çizimler insan incelemesi bekliyor.

## Sonraki adım

Önce bu dört çizimin kesit ve ölçü yerleşimlerini incelemek. Özerklik için ana sorun artık yalnızca veri biçimi değil: model ölçü uçlarını yanlış eşleştiriyor. Bu veri seti üzerinde ölçü bağlantısı/evidence denetimini güçlendirmek ve gerekirse kontrollü başka model karşılaştırması yapmak gerekir. Doğru Excel'e sıfır eklemek veya değerleri değiştirmek çözüm değildir. Genel pafta yerleşimi ve bağımsız JPEG-plan doğrulaması hâlâ eksik.
