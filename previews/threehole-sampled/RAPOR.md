# 3deliklipleyt — temsilci satır denemesi

Haiku 5.5 / high reasoning ile iki API çağrısı yapıldı; otomatik ek çağrı yok.
40 ürünün 39 benzersiz nominal örneğinden 12 temsilci seçildi. İki çağrıda aynı
12 satır kullanıldı; üretilen geometri ve ölçü fonksiyonları 40 satırın tamamında
çalıştırıldı. Modelin döndürdüğü kod elle değiştirilmedi.

## Sonuç

- 40/40 geçerli, tek katılı STEP; STEP dışa/içe aktarım kontrolü geçti.
- 40/40 STEP içinde montaj yüzeyi etiketi doğrulandı.
- 40/40 ölçülendirilmiş JPEG; toplam 312 ölçü yerleştirildi.
- Çözülemeyen ölçü: 0. OCR ile doğrulanamayan etiket: 0.
- F=0 olan 8 üründe F ölçüsü gizlendi; E deliği merkezde korunuyor.
- Bağımsız kontrolde bütün ürünlerin dış çapı, derinliği, üç deliğin merkez/çapı,
  montaj yüzeyinin iç düzlemi ve alanı doğrulandı. Bu kontrol her profil ayrıntısının
  doğruluğunun tam kanıtı değildir. Dört örnek pafta ayrıca görsel incelendi.
- 25 örnekleme kontrolü ve 77 mevcut Excel sunum kontrolü geçti; derleme başarılı.

## Token ve maliyet

| Çağrı | Input | Görünür output | Reasoning | USD |
|---|---:|---:|---:|---:|
| Geometri | 12.507 | 1.878 | 27.857 | 0,0161182 |
| Ölçü bağlama | 14.372 | 2.459 | 17.914 | 0,0116237 |
| Toplam | 26.879 | 4.337 | 45.771 | 0,0277419 |

Görünür output, sağlayıcının completion token sayısından reasoning çıkarılarak
hesaplandı. Completion sınırı her çağrıda reasoning dahil 65.536 idi.
Gönderilen tablo 42.917 → 12.912 UTF-8 bayt: %69,9 azalma. JPEG/sözleşme aynı;
bu oran toplam input veya toplam maliyet tasarrufu değildir. Aynı girdiyi 40 satırın
tamamıyla yeniden gönderip ücretli karşılaştırma yapılmadı.
İlk sandbox denemesi proxy bağlantısında engellendi; modele ulaşmadan durdu.
Ağ erişimiyle yeniden başlatılan canlı çalışma iki başarılı API çağrısıyla tamamlandı.

## Seçilen ürünler

- 11-30-13
- 11-30-260
- 11-30-27
- 11-30-318
- 11-30-81
- 11-30-894
- 11-30-895
- 11-30-9
- 11-30-905
- 11-30-908
- 11-30-913
- 11-30-989

Seçim genel kapsama kuralları ve sayısal çeşitlilik üzerinden yapıldı; önceki
elle önerilen listeyle birebir aynı değildir. Politika ve gerekçeler
`sampling-report.json` ile `../../docs/model-row-sampling.md` içinde.
12 hedefi yumuşak kotadır; zorunlu farklı durumlar daha çoksa örnek sayısı artar.

## Dosyalar

`step-jpeg.zip` 40 STEP, 40 JPEG, bu rapor ve ürün/örnekleme/token kayıtlarını içerir.
`input.zip` özgün kullanıcı girdisidir. Ortak betikler, referanslar ve yerel raporlar
bu dizindedir. Sağlayıcının iç reasoning metni yayımlanmadı.

## Sınırlar

Bu deneme aynı taslak ailesinde örneklemenin çalıştığını gösterir. Gelecek
satırlardaki bütün kombinasyonları garanti etmez. Özellikle modelin `_geometry`
fonksiyonu B=2G kontrolü içeriyor; bu grupta 40 satırın tamamı bu eşitliği sağlıyor.
Bu, yazılımın bütün gelecek taslaklara koyduğu bir kural değildir. Farklı bir
taslak/girdi yeni ortak kod üretir. Örneklenmeyen satırdaki çelişki ancak üretilen
kod veya yerel kontroller yakalarsa raporlanır.
