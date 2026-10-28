# taslak2.xlsx + taslak2guncel.jpg — müdahalesiz çalışma denemesi

## Sonuç

Gerçek girdiler dört ürün satırı içeriyor: 11-30-212, 11-30-200, 11-30-92, 11-30-381. 83 satırlık yapay test bu işlemle ilgili değildir. Bu çalışmada yeni JPEG üretilmedi. Yeni OCCT/SVG backend kademeli kesiti ve şema v2 koşullu özellik yürütmesini desteklemediği için doğru şekilde engellendi. Girdiyi zorla X=0 kesitine çevirmedi. Kullanıcıdan veya asistandan sorulara cevap alınmadı.

## Model ne anladı / nerede hata yaptı

- R8, 33 mm, 3 mm sabitlerini ve yeşil ölçülerin gizlenmesini çıkardı.
- Üçüncü delik için E/F boş ve F=0 ayrımını tanıdı.
- Kesit A-A'nın kademeli olduğunu tespit etti ve yazılım kısıtı olarak raporladı.
- Dört satırın tamamını gören yanıtta bile B/2 simetrisini varsaydı; alt delik ifadesini geçersiz `minus B/2` biçiminde yazdı. Yerel ifade doğrulaması bunu reddetti.
- F yönünü bu yanıtta pozitif verdi; bu, taslaktaki sol tarafa göre ayrıca gözden geçirilmesi gereken model yorumudur. Yön/işaret doğrulaması genel görüntü-geometri eşleştirmesinde henüz tamamlanmadı.
- Toleransları ayrı sütunlara ayırma önerisi bu dosya için gerekli değil: yerel ayrıştırıcı mevcut biçimleri okuyor. Raporda bu önerinin yerine doğrulanmış açıklama eklendi. Origin=model kayıtları kesin girdi hatası sayılmaz.

## Asistanın bu turdaki müdahaleleri

1. API şemasına soru yerine issues/hata raporu sözleşmesi eklendi; kullanıcıya soru yöneltilmez.
2. İlk çağrıdaki örnekleme, benzer boşluk düzenine sahip 11-30-92'yi örneklerden dışarıda bırakmıştı. Bu yazılım kusuru düzeltildi: sekiz veya daha az satırın tamamı gönderilir. İlk çağrı 0,031720 USD.
3. İkinci çağrı dört satırın tamamıyla yapıldı (0,034054 USD). İki çağrının toplamı 0,065774 USD. Sonrasında yeni API çağrısı yapılmadı.
4. Model planı ve sayısal değerler elle değiştirilmedi. Yeni rapor yerel kontrollerle tekrar değerlendirildi; kaynak/Excel SHA256 bağları doğrulandı. Engellenmiş durum çıkış kodu 2 ile sınandı.
5. Şema v2 grubu şu anda analiz/rapor aşamasıdır; otomatik çizim yürütücüsü tamamlanmış gibi sunulmuyor. Geçerli eski v1 örnekleri ile aynı kapsamda değildir.

## Bir sonraki adım

Öncelik: model-geometri sözleşmesini sıkılaştırmak. Serbest `minus B/2` benzeri ifadeler yerine kontrollü ifade ağacı, ölçü-özellik bağlantıları ve işaret/yön kontrolü gerekir. Ardından isteğe bağlı deliği ve hideWhen kurallarını tüm satırlara uygulayan yürütücü ve gerçek kademeli kesit desteği geliştirilmelidir. Aynı dört ürünle tekrar sınanıp, bundan sonra 80+ satırlık gerçek veri setine geçilmelidir.

Kademeli kesit desteğinin eksikliği kullanıcı verisinin hatası değildir. Kullanıcıdan doğru taslağı veya boş hücreleri değiştirmesi beklenmez. Büküm/derinlik/kalınlık için kullanıcı girdisini değiştirmeden destek eklenmelidir. Genel her-parça otomasyon ve çakışmasız ölçü yerleşimi henüz tamamlanmadı.
