# Taslak4 — bağımsız değerli sözleşme v8

Bir JPEG + ayrıştırılmış bir Excel tablosu yazılım üzerinden gönderildi. Aynı orijinal dosyalar (SHA256 önceki tam kapsamlı JSON testiyle aynı), google/gemini-4-argon, high, tek çağrı. Modele parça hakkında ilave sözel ipucu verilmedi. Ham recipe.json elle değiştirilmedi. Otomatik ikinci çağrı yok.

| Kullanım | Önceki tam kapsamlı v7 | Yeni v8 |
|---|---:|---:|
| Input | 3.956 | 3.698 |
| Düşünme | 15.328 | 21.158 |
| Görünür çıktı (completion eksi reasoning) | 2.557 | 1.714 |
| Toplam completion | 17.885 | 22.872 |
| Toplam token | 21.841 | 26.570 |
| USD | 0,186762 | 0,236116 |
| Cache token | 0 | 0 |

Maliyet yaklaşık %26 arttı; düşünme yaklaşık %38 arttı. Bu deneme maliyet azaltma hedefini sağlamadı. Tek örnekten düşünme yükünün görsel anlama, CAD planlama veya JSON düzenleme arasında nasıl dağıldığı belirlenemez. Betik denemesi yalnız geometri istediğinden ana karşılaştırma olarak kullanılmadı. Bu denemede kesit, detay, görünüş ve ölçülendirme kapsamı korundu.

## Yeni tarif ve uygulama

- 13 geometri işlemi, 14 ölçülendirme kaydı, 3 görünüş, 1 kesit ve 1 detay geldi.
- Yardımcı parametre ağacı yerine doğrudan sütunlar ve tekrar edebilen yerel aritmetik ifadeler kullanıldı. İşlem bağlantıları body/tool/sketch/seed/additions alanlarıyla verilir. Betik yok.
- Yazılım üç Excel satırını da çözdü. OCCT üç geçerli tek katı, STEP geri-okuma kontrolü ve üç JPEG önizleme üretti. Yerel yürütmede API çağrısı 0.
- 89 C# kontrolü geçti, derleme başarılı. Bunlar görselin eksiksiz doğruluğunu kanıtlamaz.

## Gözlemler ve sınırlar

- Üst/alt delikler C/2 ve -C/2; manşon merkezi -B. B=0 olan satırda manşon mevcut ve merkezde kalıyor.
- R8/R5/R1,5 ve R2 ayrı geometri işlemleri olarak uygulanabildi.
- B/G/I ölçülerini model siyah döndürdü; taslaktaki yeşil kullanımını doğru korumadı. Kod bu yanıtı elle düzeltmedi.
- Kesit main=cup_outer ekseni, through içinde delikler ve manşon var. Mevcut yerel kesit üreticisindeki eksen-orijini/kademe birleştirme sınırı nedeniyle manşon kesiti ve detay eksik/parçalı görünebilir. Bu görüntü, modelin geometriyi üretmediğinin kanıtı değildir.
- F yorumu doğruluk/maliyet değerlendirmesinin ana ölçütü yapılmadı; kullanıcı taslakta daha açık belirtilebileceğini söyledi. Model girdisine F yönü hakkında ek talimat eklenmedi.
- JPEG'ler mevcut inceleme paftasıdır: taslak anteti/yerleşimi ve ilişkilendirilmiş ölçü okları tamamlanmış değildir; değerler tabloda gösterilir. Bunlar bu değişiklikle düzeltilmiş sayılmaz.

Sözleşme: contracts/cad-v8.md; tam model talimatı: request-prompt.txt. Modelin tam özel API yanıtı bulut output klasöründe korunur; bu pakette gizli reasoning metni veya API anahtarı yoktur.
