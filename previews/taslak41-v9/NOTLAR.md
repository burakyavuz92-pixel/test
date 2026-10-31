# Taslak4.1 — detay görünüşsüz v9

Yeni ZIP'teki taslak4.1.jpg ve taslak4.xlsx yazılıma verildi. JPEG ve Excel değiştirilmedi. Aktif v9 prompt/sözleşmesinde detay görünüşü yok; genel kesit/profil talimatı da geri alınmış durumda. Ek sözel geometri ipucu yok.

Claude Sonnet 5.5, high; tek API çağrısı. Input 9825, reasoning 8168, görünür completion 2205, toplam completion 10373. Maliyet 0,123380 USD; cache 0. Komut başlangıcından API yanıt dosyasının kaydına yaklaşık 90 saniye; salt düşünme süresi değildir.

Üç satırdan üç geçerli tek katı, STEP yeniden okuma kontrolü ve üç JPEG inceleme önizlemesi çıktı. Ham tarif elle düzeltilmedi. Yazılıma müdahale veya ek API çağrısı yapılmadı. Çıktıda detay görünüşü ve details alanı yok.

## Önceki denemeler

| Deneme | Reasoning | USD |
|---|---:|---:|
| Eski taslak4 / sade v9 | 7141 | 0,114974 |
| Eski taslak4 / ek genel kesit talimatı | 11845 | 0,165160 |
| Yeni taslak4.1 / detaysız v9 | 8168 | 0,123380 |

Yeni deneme sade eski v9'a göre yaklaşık %7,3 pahalı ve reasoning yaklaşık %14,4 fazla. Ek genel talimatlı denemeden daha ucuz. JPEG ve sözleşme birlikte değiştiği ve her koşul tek örnek olduğu için bu tablo detay görünüşünün tek başına etkisini ayırmaz. Detayı kaldırmanın reasoning'i kesin düşürdüğü söylenemez.

## Geometri gözlemleri

- F ilk kez açıkça recess/cut olarak dönmüş: gövde z=0..3, D çaplı kesici z=0'dan +F kadar malzeme çıkarıyor. Önceki dışa kabartma yorumundan farklı.
- Ardından collar/add z=0'dan E'ye kadar J+4 çaplı silindir ekliyor, J çaplı delik açıyor. Dolayısıyla boşaltmanın bir bölümü sonraki eklemeyle yeniden doluyor. Kalan boşaltma halka biçiminde; F'nin kesici yönü düzelse de nihai ağız profilinin taslakla tam eşleştiği kabul edilmemeli. Bu model yorumuna elle müdahale edilmedi.
- Üst/alt delikler ±C/2, manşon x=-B. B=0 olan satırda manşon merkezde kalır.
- A/C/D/E/F/J siyah, B/G/I yeşil dönmüş. R8/R5/R1,5 gövde profilinde var. Yeni JPEG'de eski ayrı detayın R2 sayısal etiketi bulunmadığından, R2'yi önceki girdi varmış gibi zorlamadık.
- Antet, ilişkilendirilmiş ölçü okları, delik merkez çizgileri ve sayfa ölçek/yerleşim eksikleri mevcut inceleme yürütücüsünde sürer. JPEG'ler üretim paftası değildir.

Öneri: önce yeni ağız geometrisinin kalan halka biçimini kullanıcı değerlendirsin. Reasoning artışını yalnız detay görünüşüne bağlayacak kanıt yok; bu aşamada yeni prompt uyarıları veya otomatik ek çağrı eklenmedi.
