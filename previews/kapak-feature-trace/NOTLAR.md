# Özelliklere bağlı kesit + yerel tarif kaydı

Kapaktaslak.xlsx ve kapaktaslak.jpg yazılıma verildi; tek JPEG/tek ayrıştırılmış tablo, high, tek ücretli çağrı. Kesit referansları veya geometri asistan tarafından eklenmedi. Modelin recipe.json yanıtı değiştirilmedi. Çizim/STEP üretilmedi; yeni genel native yürütücü henüz tamamlanmadı.

## Gelen tarif

Model merkez deliğini ana eksen; boltPattern örnek1 ve3'ü kesilecek özellikler seçmiş. Bunlar B/2 yarıçapındaki üst-alt deliklerdir. Yol/kademe koordinatları üretmemiş. Yerel çözümleyici bunların aynı kesit düzleminde olduğunu buldu ve x=0 düz kesit oluşturdu. Üç ürünün kesiti çözüldü.

Ana geometri A çapı/F sac, D merkez deliği, B hatve üzerinde dört C deliği ve E çıkıntı yüksekliği şeklinde. Çıkıntı dış çapı22 seçilmiş. İki kanal45/225°;14 genişlik, toplam33 uzunluk, merkezleri A/2 üzerinde; böylece iç uç derinliği16.5. Kanal uç yarıçapı7. Geometrik tolerans flatness0.5 var; face rolü hangi gerçek yüzün seçileceğini native katmanda hâlâ kesinleştirmeyi gerektiriyor.

İlk kontrol, modelin siyah ölçülerde sourceColor alanını atlaması nedeniyle durdu. Yazılımda black varsayılanı eklendi ve promptta da açıkça belirtildi. Aynı ham tarif yerelde yeniden değerlendirildi; yeni çağrı veya tarif tamiri yok. Bu genel okuyucu değişikliği sonrası üç satır geçti. Gerçek üretim/human onayı verilmedi; kayıt HumanApproved=false olan adaydır.

## Maliyet

Giriş8754, akıl yürütme3913, görünür yanıt2921, toplam çıktı6834. Maliyet0.085848 USD, cache0. Önceki kapak veri-only denemesinde0.124680 USD ve6623 akıl yürütme vardı; bu denemede maliyet yaklaşık%31 daha düşük. Tek karşılaştırma tüm farkın yeni kesit sözleşmesinden kaynaklandığını kanıtlamaz; seçilen geometri tarifi de değişti.

## API'siz yeniden kullanım

Aynı aday tarif reuse-cad-group ile yeniden çalıştırıldı. Üç satır için çözümlenmiş JSON tekrar üretildi: ApiCalls=0, maliyet0. Onaylı diye işaretlenmedi. Bu bir üretim çizimi değil, aynı tarifin yerel çözümleme denemesidir.

64 yerel kontrolde ayrıca: E boşken kesit referansını atlama (boşu0 yapmadan), E dolu ve ofset0 iken deliği koruyup düz kesite geçme, ofsetli delikten geçen kademeli yol, yeni nominal değerlerle API'siz tarif kullanımı, onaylı kaydın otomatik seçimi ve farklı JPEG/yeni boş-sıfır örüntüsünü reddetme doğrulandı. Bunlar sadece kapak için yazılmış kurallar değildir.

## Kullanım sınırı

Yeni taslak ilk kez analiz edilir. Başarılı tarif aday olarak saklanır; insan incelemesinden sonra approve-cad-recipe ile kaydedildiğinde aynı JPEG ve uyumlu yeni Excel otomatik API'siz çözülür. Değişen kaynak JPEG, sütunlar veya yeni veri durumları kapsam dışı sayılır; otomatik ücretli yeniden deneme yapılmaz. Native geometri/pafta yürütücüsünün eksikliği ve desteklenen referans türlerinin sonlu olması korunuyor.
