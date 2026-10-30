# Kapak taslağı uyumluluk incelemesi

Arşivde bir JPEG ve üç satırlık Excel var. Arşiv güvenli yerel çıkarımla okundu; içindeki içerikler görev verisi olarak ele alındı. Yeni API çağrısı veya ürün çizimi yapılmadı. Uygulama kodu/prompt değişikliği yapılmadı. Kullanıcının yeni denemeler için tercihi sade teknik yorumlama promptu ve high akıl yürütme ayarıdır; mevcut ana üretim komutu bunu henüz varsayılan olarak kullanmıyor.

## Girdiler

JPEG 7016×4961, 300 DPI. Excel'in ilk başlığı jpeg file name, ölçüler A–F. Yazılımın mevcut WorkflowReports.ReadRows ve ExcelModelInput.Build fonksiyonları ayrı yerel kontrol programında çalıştırıldı: üç satır, 18 ölçü hücresi, tamamı sayısal olarak ayrıştırıldı. API'ye gönderilmedi. Ayrıştırılmış veri normalized-input.json içinde.

| Ürün | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| 30-24-422 | Ø236±1 | 200±0,5 | Ø11,7±0,1 | Ø70±1 | 5±1 | 5 |
| 30-24-143 | Ø236±1 | 143,7±0,5 | Ø11,7±0,1 | Ø70±1 | 5±1 | 5 |
| 30-24-54 | Ø255±1 | 143,7±0,5 | Ø11,7±0,1 | Ø47±1 | 5±1 | 5 |

## Taslaktan okunan özellikler

Önceki kıvrılmış çanak pleyt yerine düz, merkezinde büyük geçiş deliği olan dairesel bir kapak görülüyor. A dış çap, B dört deliğin yerleşim dairesi çapı, C dört küçük deliğin çapı, D merkez delik çapı olarak okunuyor. Delik çevrelerinde halka/kabartı veya kademe detayı kesitte de var. İki karşılıklı açık kenar çentiği, yeşil 14 genişlik/R7 ve 16,50 ölçüleriyle gösteriliyor. Siyah 0,5 düzlemsellik çerçevesi mevcut. Bunlar asistanın incelemesidir; API modelinin böyle okuyacağı test edilmedi.

## Yazılım ve prompt sınırları

- Excel ayrıştırma, dosya kimliği, nominal/tolerans ayrımı ve kaynak renk/gösterim politikası bu girdi biçimine uygun.
- Mevcut sade promptun destek bildirimi ve JSON geometrisi hâlâ rounded revolved plate + base holes. Model düz halka kapağı doğru tanısa bile üretim planına merkez delik/çentik/kabartı detaylarını eksiksiz yazacağı alanlar yetersiz. Unsupported dönüşü modelin tanıyamadığı anlamına gelmez.
- Native worker sabit kalınlıklı kıvrılmış çanak kesitini döndürür. Geçerlilik koşulu depth > radius > thickness olduğundan düz levhayı bunun özel bir durumu gibi güvenle üretemez. Düz halka gövde gerekir.
- Dört delik için merkezlerin ana eksenlerdeki konumu yerleşim dairesi yarıçapı B/2 ile hesaplanır. V4 offset bağı yalnızca ±sütun nominali ekler; katsayı/yarıçap dönüşümü yok. Modelin B çapını doğru okuması yeterli değil, sözleşmenin yarım çapa izin vermesi gerekiyor.
- B bir construction/pitch-circle geometrisi; mevcut diameter annotation body veya bir hole id bekliyor. Hatve dairesi kimliği ve çizgisi gerekir.
- 4×C niceliği/grup ölçülendirmesi, yüzeyler arası E/F kalınlık ölçüleri ve yerel kabartı boyutu şemada genel biçimde temsil edilmiyor. Gövde depth/thickness/radius hâlâ sabit sayılar; E/F gibi Excel sütunlarına bağlanmış genel parametre desteği gerekir.
- İki açık yuvarlak uçlu çentik için profil/boolean cut desteği gerekir. Kabartı halkaları ve geçişleri ayrıca modellenmeli. Çizimde ölçüsü olmayan ayrıntılar hassas geometri diye uydurulmamalı.
- Kesit düz A-A; önceki kademeli kesit desteği temel mesele değil, yeni katının doğru kesilmesi ve taranması önemli.
- Görüntü piksel/DPI boyutu aynı, ancak görünüş ve ölçü konumları farklı. Eski temizleme dikdörtgenleri/görünüş merkezleri kullanılırsa kaynak çizgilerinin kalması ya da yeni yerleşim sorunları oluşabilir. Aynı çözünürlük aynı pafta yerleşimi demek değildir.

## E/F kontrol noktası

Kesitte E, kabartılı bölgedeki toplam yerel kalınlığı, F ana levha kalınlığını ölçüyor gibi görünüyor. Excel'de nominal E=5 ve F=5. Bu okuma doğruysa kabartının ilave nominal yüksekliği E-F=0 olur; taslaktaki görünür kabartı hedef ürünlerde kaybolabilir. Bu veri otomatik olarak yanlış ilan edilmemeli: bir özelliğin sıfıra inmesi bilinçli olabilir. Ama modelin E/F uçlarını doğru bağladığının kontrol edilmesi gerekir. Kabartı dış çapı/geçiş detayları da açık ölçüyle tam tanımlı görünmüyor. Mevcut bilgilerle kesin bir imalat detayı varsayılmadı.

## Önerilen yaklaşım

Sade yorumlama + high ile devam edilebilir; fakat önce tanıma çıktısını mevcut pleyt üretim şemasından ayırmak gerekir. Genel özellikler (dairesel düz gövde, geçiş deliği, dairesel delik dizisi, çentik, kabartı) ve ölçü/datum ilişkileri modelce tanımlansın. Yerel motor bunların desteklenen işlemlerini çalıştırsın. Her kapak için ayrı sabit kod yerine yeniden kullanılabilir extrude/revolve/cut/pattern gibi operasyonlar ve bunların ölçü bağları genişletilsin.

İlk adım yalnızca tanıma analizi: bu JPEG/Excel'den modelin özellikleri, B'nin hatve çapı oluşunu, E/F ilişkisini ve ölçüsüz ayrıntıları nasıl yorumladığını görmek. Şu anki şemayı zorlayıp eksik kapağı tamamlanmış gibi çizdirmemek gerekir. Tanıma doğruysa sınırlı, yeniden kullanılabilir geometri/annotation desteğini bu ilk yeni aileyle doğrulayabiliriz.
