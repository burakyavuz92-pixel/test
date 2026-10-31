# Elle düzeltilmiş tarifle yürütücü kapasite testi

API çağrısı yapılmadı. Haiku no-colors tarifinin ayrı bir kopyası elle düzeltildi. Orijinal API yanıtı ve üretim kodu değiştirilmedi. Önceki arka dış kök R2 işlemi çıkarıldı; bütün yapım işlemlerinin ardından ön recess tabanı z=-F ile J çaplı iç silindirin ortak kenarına R2 eklendi. Ölçü referansı yeni işlem ID'sine bağlandı. Başka geometri düzeltilmedi.

Bu, modelin kendiliğinden doğru tarif verdiği bir çalışma değildir; elle oluşturulan aday doğru konumun mevcut yürütücüde işlenebilmesini test eder. Ön taraftaki delik geçişini oluşturmak için yeni primitive gerekmedi. Bu adayın taslaktaki bütün deformasyon/et kalınlığı ayrıntılarını sağladığı iddia edilmez.

Üç satırda native üretim ve STEP yeniden okuma kontrolleri geçti; 3 JPEG ve 3 STEP üretildi. İlk ürünün R2 yüzeyi gerçek CAD geometrisinden ölçüldü: torus merkezi [-73,0,-2.5], büyük yarıçap 12.25, küçük yarıçap 2 mm. Eski yanlış kök yüzeyi [-73,0,-5], 15.25/2 idi. R2 artık ön delik geçişinde, farklı bir yüzdür.

r2-closeup.svg: delik ekseninden geçen düz kesitin geometrik çizgileri; normal paftanın kademeli kesit sunumundan bağımsızdır. Bu görüntü gösteriminde ek bir katı düzeltmesi yoktur. STEP ve yakın kesit aday konumu incelemek için verilmiştir. Genel paftanın antet/ölçü oku/kesit çizgisi sınırları devam eder.
