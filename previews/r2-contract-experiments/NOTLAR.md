# R2: üç kontrollü sözleşme denemesi

Hepsinde aynı taslak4.3.xlsx ve taslak4.2.jpg, Haiku 5.5 high, token tavanı 65536 kullanıldı. İlk üç denemede üç tam geometri API çağrısı yapıldı; yanıtlar elle değiştirilmedi. Her denemede üç JPEG ve üç STEP oluştu. İlk üç denemenin maliyeti 0,0551785 USD. Sonraki dar bölge teşhisiyle birlikte toplam dört çağrı ve 0,0566369 USD. Cache indirimi yok.

| Deneme | Değişiklik | Reasoning token | Maliyet USD | R2 |
|---|---|---:|---:|---|
| A | Kenar noktası yerine iki analitik yüzün ortak kenarı | 33386 | 0,0187354 | Aynı arka dış kök |
| B | A + ok ucunun görsel konumu ve kısa bölge tanımı | 31096 | 0,0177154 | Aynı arka dış kök |
| C | Kesitteki radyusları kenar seçimi yerine doğrudan profil yayıyla kurma | 33130 | 0,0187277 | Aynı arka dış kök |

## Somut bulgu

İlk ürünün üç native katısında da R2 yüzeyi ölçüldü: torus merkezi [-73,0,-5], büyük yarıçap 15,25 mm, küçük yarıçap 2 mm (C'de sayısal yuvarlama farkları var). Dolayısıyla yalnız resme bakarak değil, CAD yüzleri üzerinden aynı konum doğrulandı. C'de R2 için fillet seçicisi kullanılmıyor; yay doğrudan revolve profilinde tarif edilmiş. Bu sonuç, hatanın yalnız near sözcüğünden veya native kenar seçicisinin yanlış seçiminden kaynaklandığı açıklamasını desteklemiyor.

B'de model sourceMark.arrowTip=[0.168,0.376] döndürdü; 7016×4961 görüntüde yaklaşık [1179,1865] piksel. Bu işaret R2 okunun bulunduğu ön geçiş bölgesine yakın. Ancak location alanı 'hub outer surface junction with plate inner face' ve yüz çifti z=-3 düzlemi + (J+6)/2 yarıçaplı silindir. Yani görüntü üzerinde işaretlenen bölgeyle kurulan geometrik ilişki uyuşmuyor. Yaklaşık işaretleme tek başına doğru geometrik anlama kanıtı değildir.

## Sonuç ve sınır

R2 çözülmedi. Sözleşmenin daha ilişkisel olması veya doğrudan profil yayı kullanması tek başına bu örneği düzeltmedi. Modelin fiziksel geçişi yorumlaması ile onu yapım tarifine aktarması arasında yanlış eşleştirme sürüyor. Bu üç deneyden modelin iç düşüncesinin kesin nedeni çıkarılamaz. Başlangıçtaki 'yazılım doğru veriyi yanlış yere uyguluyor' açıklaması için kanıt yok; modelin tarif ettiği yeri yazılım sadakatle oluşturuyor.

Geçici sourceMark alanı ve profil yöntemini zorlayan talimat etkin prompt/sözleşmeye alınmadı. Normal üretim promptu ve sözleşmesi deney öncesine döndürüldü; bu sonuç bir çözüm gibi yayımlanmadı. İki-yüz seçici kodu ve deneysel sözleşme ayrı saklandı, eski nokta seçimi okunmaya devam eder. Üretim girdilerine R2 konumu eklenmedi; ürün özelinde koordinat sabitlemesi yapılmadı. Mevcut operation alanı uyuşmazlığı deney öncesi etkin sözleşmede hâlâ bilinen bir sorundur; bu denemeler onu çözülmüş saymaz.

## Sonraki anlamlı ayrım

Yeni bir genel uyarı daha eklemek yerine tek bir yerel R2 kesit bölgesinde, geometri kurdurmadan, okun iki yanındaki malzeme/boşluk sınırının nasıl görüldüğünü ayrı bir teşhisle çıkarmak gerekir. Sonrasında bu 2D sınırın oluşturulan 3D yüzlerle eşleşmesi denenebilir. Bu ayrım için aşağıdaki dördüncü teşhis yapıldı; bütün geometriye tekrar tekrar aynı çağrıyı yapmanın yararı ilk üç deneyde gösterilmedi.

## Yerel kontroller

Yeni seçici iç/dış dairesel kenar ayrımını, olmayan yüz çiftini reddetmeyi ve uçtan uca fillet üretimini test ediyor. 4 yeni seçici testi, 13 mevcut v9 testi, 9 native testi ve C# kontrolleri geçti. Bunlar modelin R2'yi doğru yorumladığı anlamına gelmez. Ham özel reasoning kayıtları yayımlanmadı.

## D — yalnız yerel kesiti okuma

Orijinal 7016×4961 JPEG'den [850,1450,1850,2500] kutusu araştırma sırasında elle seçilerek kırpıldı. Bu bölgeyi otomatik bulan bir üretim özelliği yazılmadı. Tek kırpılmış JPEG, CAD tarifi/Excel/üretim sözleşmesi olmadan aynı Haiku high modeline gönderildi; yalnız R2 okunun hedefi, komşu sınırlar ve belirsizlik soruldu. Bu, normal yazılıma ham Excel+JPEG vererek yapılan bir üretim denemesi değildir. Teşhis betiği ayrı araştırma çağrısıdır.

Input 1559; reasoning 2042; görünür çıktı 563; maliyet 0,0014584 USD. Yanıt R2 okunu yaklaşık (330,408) kırpım pikselinde buldu. 'Hub inner bore surface' ile plakadaki delik konturu arasındaki geçişi tarif etti; J+6 dış köküne bağlamadı. Çap referanslarını tam uzlaştıramadığını belirtti; bazı sol ölçü yazıları kırpımda kesik. Bu nedenle bunu eksiksiz ölçü çözümü gibi sunmuyoruz.

Bu çıktı yerel konturun, CAD yapım tarifi istenmediğinde farklı okunabildiğini gösteriyor. D'de hem görüş alanı hem görev değişti; yalnız kırpma veya yalnız sözleşme değişikliğinin kesin etkisini kanıtlamıyor. Yanlışlığın tam nedeni bulundu/üretim düzeldi iddiası yok. Sonraki anlamlı deney, yerel sınır okumasının doğru yüz/profil referansına çevrilmesini ayrı kontrol etmek; kullanıcıdan yeni CAD/koordinat istemek değil. Bu tur dört çağrıda sonlandırıldı, otomatik döngü yok.
