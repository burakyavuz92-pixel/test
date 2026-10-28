# OCCT ilk deneme — 11-30-212

[İzometrik JPEG](11-30-212-occt.jpeg) · [STEP modeli](11-30-212-occt.step)

Bu görüntü önceki el çizimi motorundan değil, OCCT'nin oluşturduğu gerçek 3B katıdan elde edildi. Örnek: dış çap 160 mm, toplam derinlik 33 mm, sabit cidar 3 mm, dış R8/iç R5; 10/10/5 mm çaplı üç delik. Konumlar (0,44.45), (0,-44.45), (-44.5,0). Veriler önceki örnek satırdan açıkça girildi; bu denemede API ile resim yorumlama yapılmadı.

Modelin geçerli ve tek katı olduğu, deliklerin beklenen hacmi çıkardığı ve STEP dosyasının tekrar açıldığında aynı hacmi koruduğu doğrulandı. Görüntü VTK ile bilgisayarın CPU'sunda (Mesa llvmpipe) üretildi. API çağrısı veya dış CAD servisi yok.

Bu 1400×1100 JPEG yalnızca görüntü kalitesi/bakış açısı denemesidir; ölçülendirilmiş pafta değildir. Renk, ışık ve kamera değiştirilebilir. Deliklerden bakış doğrultusuna göre arka iç duvarın görünmesi gerçek derinlik hesabının sonucudur. Görüntüleme 0,08 mm ağ toleranslıdır; STEP analitik geometriyi korur. Kesin geometri ve görsel onay henüz kullanıcı tarafından verilmedi. Windows'a dağıtım henüz test edilmedi.

Mevcut teknik resim üretimi değiştirilmedi. Beğenilmezse OCCT komutu kullanılmaz ve önceki yöntemle devam edilir.
