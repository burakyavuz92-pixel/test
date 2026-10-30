# Taslak4 v9 — kesit profilini birlikte yorumlama talimatı

## Deney

Sözleşme, model/high ayarı, JPEG ve Excel aynı kaldı. Prompta tek genel yaklaşım eklendi: kesit malzeme/boşluk sınırlarını diğer görünüşlerle yorumlamak ve bağlantılı ölçü/radyusları birlikte taşıyan profili kullanabilmek. F/R2 yönü hakkında parçaya özel talimat eklenmedi. Görsel kırpılmadı veya değiştirilmedi; 7016×4961, 300 DPI kaynak gönderildi. Sağlayıcının görüntüyü içeride hangi çözünürlükte işlediği doğrulanmış değildir.

Claude Sonnet 5.5, high, tek API çağrısı. Otomatik tekrar/onarım yok. Ham yanıt elle değiştirilmedi. Yazılım üç STEP ve üç JPEG'i müdahalesiz üretti; BRep/STEP kontrolleri geçti. Bu, geometri yorumunun doğruluğunu kanıtlamaz.

| Kullanım | Önceki v9 | Yeni talimat |
|---|---:|---:|
| Input | 9.922 | 9.985 |
| Reasoning | 7.141 | 11.845 |
| Görünür completion (completion−reasoning) | 2.372 | 2.674 |
| Toplam completion | 9.513 | 14.519 |
| USD | 0,114974 | 0,165160 |
| Cache token | 0 | 0 |

Maliyet yaklaşık %43,6 arttı, reasoning yaklaşık %65,9 arttı. Bu tek deneme, talimatın reasoning yükünü neden artırdığını veya hangi alt işin ne kadar sürdüğünü göstermez. Ana hedef sağlanmadı.

## Geometri ve çizim bulguları

- Gövde ve manşon bu kez ikisi de revolve profil olarak yazıldı. Bağlantılı ayrıntıları tek profile taşıma yönünde bir değişiklik var.
- F yine dış çıkıntı: model gövdenin dış yüzünü z=33 kurmuş, collar profilini z=33+F'ye kadar taşırmış. Ölçü rolü de 'boss height above outer face'. Bu yalnız koordinat işaretinin değişmesi değildir; malzeme dışarı eklenir. İstenen iç boşaltma oluşmadı.
- R2 artık profil yayı ve siyah ölçü olarak var; model onu 'collar root fillet radius' yani manşon kök radyusu olarak tanımlamış. Hedeflenen iç ağız geçişinin doğru kurulduğu sonucuna varılamaz.
- A ve C bu kez siyah; önceki yanlış yeşil sınıflandırma yok. B/G/I ve sabit yeşil ölçüler gizleniyor. Bu düzelmenin talimat kaynaklı mı üretim değişkenliği mi olduğu tek çağrıdan belirlenemez.
- B=0 olan satırda merkezdeki manşon korunur. Üst/alt delikler ±C/2'de tarif edilmiş.
- Detay B ve kesit gösteriminin önceki yerel odaklama/sunum sınırlamaları sürüyor; bu testte onlara müdahale edilmedi. Antet ve ölçü okları mevcut inceleme düzeninde, üretim paftası tamamlanmış değil.

## Sonraki öneri

Bu sonucu başarı sayıp promptu yeni uyarılarla büyütmeyelim. Bir sonraki ayrı teşhis deneyi, detayın malzeme/boşluk yorumunu CAD sözleşmesi üretmeden sınayabilir. Bu, varsa görsel yorum sorunu ile CAD'e çevirme sorununu ayırmaya yardımcı olur; bu çalışma sırasında ek çağrı yapılmadı. Yeni prompt metni sürümlendi; verim kazancı iddiası yok.
