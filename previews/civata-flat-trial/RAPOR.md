# Cıvata 730001 — Phong / Flat denemesi

Aynı mevcut STL, aynı kamera [1,1,1], aynı ışık, renk, parlaklık ve kontur ayarları.
Yalnız VTK interpolation modu değiştirildi. Geometri ve STEP değiştirilmedi; API
çağrısı yok. Üretim varsayılanı Phong olarak korundu. Flat, render verisinde
rendering.shading=flat seçeneğiyle denendi; ana akışa varsayılan yapılmadı.
Flat üçgen yüzlerin tonlarını ayrı hesapladığından kavislerde çokgen/faset görünümü
oluşabilir. Bu seçenek gerçek CAD kenar çizgilerini eklemez.
