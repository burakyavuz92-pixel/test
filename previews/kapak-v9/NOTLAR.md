# Kapak — v9 sözleşme ve yerel yürütücü testi

## Ne gönderildi?

Orijinal kapaktaslak.jpg + kapaktaslak.xlsx yazılıma verildi; yazılım bir JPEG ve ayrıştırılmış tek tablo gönderdi (üç satırın tamamı). Ek parça açıklaması veya geometri ipucu eklenmedi. Aktif ayar anthropic/claude-sonnet-5.5, high. Yeni ücretli çağrı sayısı 1, otomatik onarım çağrısı 0. Önceki Gemini taslak4 çağrısıyla doğrudan maliyet kıyası yapılmadı.

## Kullanım

| Ölçüm | Önceki kapak feature-trace v7 | Yeni kapak v9 |
|---|---:|---:|
| Input token | 8.754 | 9.470 |
| Reasoning token | 3.913 | 3.721 |
| Görünür completion (toplam eksi reasoning) | 2.921 | 1.738 |
| Toplam completion | 6.834 | 5.459 |
| USD | 0,085848 | 0,073530 |
| Cache token | 0 | 0 |

Kaynak JPEG ve Excel SHA256 özetleri iki çalışmada da aynı; model kimliği/high ayarı da aynı. Yeni toplam maliyet yaklaşık %14,3 düşük; reasoning yaklaşık %4,9 düşük, input artmış. Bunlar bağımsız tek örnek çağrılardır. Sağlayıcı sürümü/davranışı ve örnekleme etkisi sabitlenmiş tekrarlı deney değildir. Sözleşmenin reasoning yükünü kesin azalttığı sonucu çıkarılamaz. Asıl kazanç bu örnekte görünür çıktının küçülmesidir.

## Yazılım ve sonuç

- Sıralı tek-gövde işlemlerini yerelde iç OCCT işlem ağına çeviren v9 derleyicisi eklendi. Model bu iç ağı yazmaz.
- Kod çalıştırmayan AST ifade yorumlayıcısı: isteğe bağlı değişkenler, tembel koşullar, blank/zero ayrımı, matematik/trigonometri. Python eval/exec yok.
- Profil içi boşluk, from/to ekstrüzyon, yerelde bounds üzerinden throughAll, box/cylinder/revolve, polar/linear kopyalar ve mevcut fillet yolu bağlandı. Modeller Python betiği döndürmez.
- 5 ortak geometri özelliği (plate, boss, centerHole, holes, slot), 9 ölçü kaydı, 3 görünüş, 1 düz kesit, 1 düzlemsellik kaydı geldi.
- Üç satırda geçerli tek katı ve STEP yeniden okuma kontrolleri geçti. Üç STEP ve üç 1754×1240 JPEG önizleme üretildi. Kaynak DPI korunur. Yerel yürütme API çağrısı 0.
- 92 C# kontrolü, 9 yeni v9 Python kontrolü ve 12 mevcut native kontrol geçti. Bunlar bütün sözleşme kombinasyonlarının veya taslakla eşleşmenin kanıtı değildir.

## Müdahale kaydı — ham model verisi değiştirilmedi

1. İlk API yanıtı saklandı; çözümleme düz kesit alanlarında yazılım hatasıyla durdu. Yeni point/normal alanlarının eski yerel plane yapısına dönüşümü eksikti. Genel adaptör düzeltildi; regression kontrolü eklendi.
2. Aynı yanıtın yerel tekrarında geometri/STEP oluştu, çizim modülü nominal alanını beklerken derleyicinin value alanı vermesi nedeniyle JPEG üretimi durdu. Genel alan eşlemesi düzeltildi; regression kontrolü eklendi.
3. Aynı recipe.json, aynı kaynaklar ve aynı model tarifinin yerel tekrarından üç JPEG alındı. Ek API çağrısı ve elle geometri/tarif düzeltmesi yok.

İlk çalışma raporu blocked durumuyla korunmuştur; son başarı native-results.json/render-report.json içindedir. İlk başarısız koşular output/kapak-v9 ve output/kapak-v9-native, son koşu output/kapak-v9-final. Yeni yazılım bu iki adaptör düzeltmesini içerir.

## Görsel değerlendirme ve öneri

- Dört delik, hatve çemberi yerleşimi, merkez açıklığı ve karşılıklı iki çentik üç varyanta uygulandı. E yüksekliği F levhasının üzerine eklenmiş; boyun dış çapı modelin tamamlaması olarak C+10. Yeşil 14 / 16,5 / R7 çıktı ölçü tablosuna basılmadı. Siyah ölçüler ve hücre toleransları korundu.
- Boyunları silindirik kabartma olarak tamamladı; taslaktaki ağız geçişi/pah benzeri küçük detaylar aynı ayrıntıyla kurulmadı. Ölçüsü verilmemiş bu detayları kesin doğru kabul etmiyoruz.
- İzometrik kamera taslaktaki dik duruş yerine daha yatay bir bakış seçmiş. Bu, yazılımda elle belirlenmiş kamera değildir; model yanıtındaki direction/up uygulanmıştır.
- Native çıktı hâlâ inceleme paftası: taslak anteti/yerleşimi, ölçü okları, delik eksenleri ve geometrik tolerans çerçevesi tamamlanmış değildir. Değerler tabloda, flatness ise metin olarak gösterilir. Bu eksikler modelin hiç veri üretmediği anlamına gelmez; yerel çizim uygulamasının kapsamıdır.
- Gerçek geometriden ölçüp Excel ile karşılaştıran yeni bir sistem eklenmedi. Mevcut BRep/STEP ve etkisiz kesici kontrolleri korundu.
- Boolean sonrası operation kökenine göre sıkı kenar izleme ve featureTrace algoritmasının önceki sınırlamaları sürer. Bu kapak yanıtı fillet veya kademeli kesit üretmediği için bu yolları doğrulamış değildir.

Öneri: promptu hemen yeniden büyütmeden aynı v9'u asimetrik ve isteğe bağlı delikleri olan taslak2 grubuyla sınamak. Geometri aktarımı yeterli bulunursa sonraki geliştirmeyi ölçü okları/eksenler ve taslak sayfa yerleşimine ayırmak. Maliyet optimumu iddiası için aynı örnek ve kapsamda tekrarlı ölçüm gerekir; şimdi ek ücretli çağrı yapılmadı.
