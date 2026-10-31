# Sabit taslak anteti — A5

Kullanıcı bütün taslaklarda antetin aynı kalacağını belirtti. Yazılım, verilen JPEG'deki sabit çerçeve, antet, logo, notlar ve revizyon alanını kullanıyor; çizim bölgeleri temizlenerek OCCT görünüşleri yeniden yerleştiriliyor. Referans yerleşim 7016×4961 JPEG'e göre normalize edilir. Bu, değişken antetleri otomatik tanıyan bir sistem değildir.

Ürün hücresindeki H, Excel A sütunundan outputId ile değiştirilir. Ölçek hücresine ana görünüş/kesitin ortak ölçeği, format hücresine A5 yazılır. Bu üç alan Arial ile doldurulur. Sabit tarih, revizyon, isimler, parça adı ve diğer notlar taslaktan aynen korunur; güncel tarih veya yeni onay uydurulmaz. Sabit antet raster olarak korunur, hücre hücre yeniden çizilmez.

Yeni API çağrısı yapılmadı. Haiku no-colors kayıtlı tarifi değişmeden kullanıldı. 3 JPEG ve 3 PDF üretildi. Geometri/R2 düzeltmesi yapılmadı. Ölçüler hâlâ geçici tabloda; çizim üzerine ölçü oku yerleştirilmesi bu adımda tamamlanmadı. Görünürlük Excel düzeni de bekliyor. Kademeli kesit görünürlüğünün mevcut sınırlamaları sürüyor.

A5 yatay yaklaşık 210×148 mm, 1754×1236 piksel, JPEG DPI yaklaşık 212. Baskıda gerçek boyut/%100 kullanılmalı. Antetin kaynakta büyük kâğıt için tasarlanmış küçük yazıları A5'te küçülür; bu örnek baskı incelemesi içindir. İzometrik ölçek dışı işaretlidir. Ölçekler 1:4 / 1:2 / 1:1,5.

İlk JPEG görsel incelendi. 2 yeni şablon testi ve mevcut 9 native test geçti; üç üründe katı ve STEP yeniden okuma kontrolleri de geçti. Yeni model yorumu veya geometri doğruluğu onayı anlamına gelmez.
