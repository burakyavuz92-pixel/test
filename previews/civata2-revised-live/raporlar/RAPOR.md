# Güncellenmiş Cıvata2 — yatay L ve R5 kafa

7 satırlı Excel ve yeni JPEG, Haiku 5.5 / high reasoning ile iki API çağrısına verildi.
Excel'in tamamı seçildi. Yeni JPEG'deki L yatay; sabit 5 parantezsiz, kafa R5 ve
1 mm bilgileri eklenmiş. Kullanıcı girdisi ve model betikleri/referansları değiştirilmedi.

## Nihai sonuç

- 7 STEP + 7 JPEG. 7/7 geçerli tek katı ve STEP aktarım kontrolü geçti.
- 7/7 montaj yüzeyi adı ve kafa altı düzlemi doğrulandı.
- Her paftada A/B/C/D/E/L: 6 ölçü, toplam 42 ölçü. Çözülemeyen ölçü ve
  doğrulanamayan etiket yok. L, Ø16 olarak radyal eğik çap çizgisiyle gösterildi.
- Sabit 5, R5 ve 1 mm geometride kullanıldı; parantezsiz oldukları için ölçülendirilmedi.
- A_METIN metni nominal A yerine basıldı; kullanıcı metinlerinden diş geometrisi
  veya standart çap türetilmedi. C'nin başında kullanıcı Ø vermediği için sayı düz.
- Ölçekler: 730001/730003/730006/730017 2:1; 730013/730014/730016 2,5:1.
- Bağımsız nominal kontrol 7/7: z boyu B+D, A/C/L çapları, D ve 5 mm boyun,
  uç pahı, R5 dairesel oluşturucu, kafa uç yarıçapında 1 mm içeri çekilme ve montaj düzlemi.
  R5 yüzeyi STEP'te SurfaceOfRevolution olarak saklanmış; oluşturucu eğri yarıçapı 5 mm.
- 14 referans ve 16 yerleşim testi geçti. Dört pafta görsel incelendi.

## Çalışmada bulunan genel destek eksikliği

L'nin OCR sorunu yeni yatay yazımla çözüldü. İlk çalışmada etiket doğrulandı;
ancak L çapı kavisli R5 yüzeyindeki en geniş daireyi işaret ediyor. Burada silindir
veya topolojik tam daire kenarı bulunmadığından önceki çap destek kontrolü L'yi
7 üründe de reddetti: 'No matching cylinder or full circular edge...'.
Modelin merkez, eksen ve yarıçapı doğrudur; model kodu elle düzeltilmedi.
Yazılıma kavisli eş eksenli dönel yüzeydeki tam çemberleri doğrulama desteği eklendi.
Çember/yüzey BRep ortak kısmının uzunluğu tam çevreyi sağlamalı; örnek birkaç nokta
üzerinden tahmin yapılmıyor. Kısmi daire, yanlış eksen/kesit veya düzlemsel yüzey
üzerindeki keyfi daire destek sayılmıyor. Parçaya özel değer veya ürün kimliği yok.

Aynı yanıtlar API'siz replay ile tekrar çalıştırıldı; bütün ölçüler bağlandı.
İlk çalışma 405,44 sn, tekrar 46,17 sn (toplam yaklaşık 7 dakika 32 sn; inceleme ve
kod düzenleme süresi hariç). initial-run-report.json ve initial-script-sheet-results.json
ilk durum; run-report.json API'siz son tekrarın durumudur. İlk koşu müdahalesiz
eksiksiz tamamlanmadı; yukarıdaki genel destek değişikliğiyle tamamlandı.
Önceki sayısal vektör sabiti desteği bu çalışmada sorun çıkarmadı.

## API kullanımı — toplam iki çağrı

| Çağrı | Input | Görünür output | Reasoning | USD |
|---|---:|---:|---:|---:|
| Geometri | 8.922 | 1.448 | 25.230 | 0,0142312 |
| Ölçü bağlama | 10.633 | 1.780 | 15.836 | 0,0098713 |
| Toplam | 19.555 | 3.228 | 41.066 | 0,0241025 |

Görünür output, completion sayısından reasoning çıkarılarak hesaplandı; çağrı başına
reasoning dahil 65.536 completion tavanı var. Ek API çağrısı yok. Sağlayıcının iç
reasoning metni paylaşılmadı. geometry-prompt.txt/measurements-prompt.txt gerçekten
gönderilen istekler; measurements-updated-contract.txt gelecekteki çağrılar için
genişletilmiş destek bilgisidir.

## Geometri yorumu

Yeni R5 ve 1 mm bilgileri önceki varsayılan 2 mm kafa yuvarlatması yerine kafa
profilini belirledi. Ölçüsü verilmeyen konik geçişin eksen boyu model tarafından
3 mm tamamlandı; bu kullanıcı ölçüsü olarak sunulmuyor. Bağımsız nominal kontroller
bütün tanımsız ayrıntıların tasarım niyetine uygunluğunun tam kanıtı değildir.

Ana klasörde tüm STEP/JPEG'ler birlikte; diğer kayıtlar raporlar/ altında.
step-jpeg.zip aynı düzeni içerir. input.zip özgün kullanıcı girdisi,
overview.png dört örneğin önizlemesidir.
