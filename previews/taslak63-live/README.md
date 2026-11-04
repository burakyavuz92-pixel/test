# Taslak6.3 — yeni API çağrılarıyla tam akış

Model `anthropic/claude-haiku-5.5`, reasoning `high`. İki yeni API çağrısı: geometri/yüz etiketi, ardından ölçü referansları. Eski STEP veya ölçü kodu kullanılmadı. Tüm dosyalar taslak6.3 girdisinden; geometri/ölçü koduna elle düzeltme uygulanmadı. Raw API reasoning yanıtları yayımlanmadı.

## Sonuç

6/6 tek geçerli katı ve STEP geri okuma başarılı. 6/6 montaj yüzeyi etiketi yazılıp geri okundu. 6/6 JPEG üretildi. **Akış sonucu `sheets-produced-with-unresolved-measurements`; tüm ölçüler bağlanmış değildir.** Beş parça 1:1, kısa 733001-03 parçası 2:1.

Her parçada 8 ölçünün 6'sı yerleşti: A, B, C, E, iki pah. D ve 25 tablodadır. Üst/alt tolerans gösterimi ve satır bazında Ø tercihi yerel veriden uygulanır; ilk üç satırda E düz, son üçünde Ø ile yazılır.

## 733001-03 karşılaştırması

D=23,8 yerine D=16 verildi. Yeni STEP toplam Z boyu 23,8 mm; Ø10,5 yüzey Z=-22,8…-16 arasında korunmuş. B ve iki pah referansı bu kez bağlanıyor. Aynı zamanda prompt +Z bilgisi de değiştiği ve model yeniden çalıştığı için tek nedenin yalnız D değişikliği olduğu kontrollü biçimde kanıtlanmış değildir.

Yeni +Z tanımıyla A tarafı Z=0'a, gövde/flanş negatif Z'ye yerleşti. Kamerayı yazılımda çevirmedik.

## Karşılaşılan sorunlar

- **D:** model başlangıç noktasını `[6,0,0]` verdi. A ucundaki 1 mm iç pah nedeniyle o düzlemde delik yarıçapı 7 mm; verilen nokta boşlukta kalıyor. Yürütücü bu noktayı parça üzerinde bulamadığı için bağlantıyı reddetti. Bu bütün satırlarda var. D=16 değişikliği tek başına modelin uç noktayı doğru döndürmesini sağlamamış.
- **25:** model merkezini konik bölgenin ortasına koydu. 733001-03 için verilen Z=-21,3; STEP'teki gerçek Ø25 tam çember Z=-18,8. Merkez farkı nedeniyle bağlantı reddediliyor. Diğer satırlarda da aynı 2,5 mm konum farkı var. Bu, önce eklenen dairesel kenar desteğinin yokluğu değil, yeni referansın yanlış konumda olmasıdır.
- **Montaj:** model bu kez düzlem yerine E/2 yarıçaplı silindirik yüzeyi etiketledi. STEP etiketinin teknik olarak korunması, kaynak okun doğru yüzeyi seçtiğini kanıtlamaz. Önceki düzlem beklentisi bakımından bu seçim ayrıca incelenmelidir; montaj için doğrulanmış yüz seçimi olarak değerlendirilmemelidir.

## Token ve maliyet

| Çağrı | Input | Görünür yanıt | Reasoning | Completion toplam | USD |
|---|---:|---:|---:|---:|---:|
| Geometri | 6752 | 713 | 22222 | 22935 | 0.0121427 |
| Ölçü | 7613 | 2422 | 11591 | 14013 | 0.0077678 |
| Toplam | 14365 | 3135 | 33813 | 36948 | 0.0199105 |

Görünür yanıt = completion − reasoning. İlgili API kullanım alanları `usage.json` içindedir. ZIP altı STEP/JPEG çiftini, ölçek/yerleşim raporlarını ve modelden gelen kod/verileri içerir. Geometrinin taslağa tam uygunluğu bu teknik kontrollerden çıkarılamaz; çıktılar inceleme amaçlıdır.
