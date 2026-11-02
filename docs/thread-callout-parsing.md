# Yerel diş çağrısı ayrıştırma

Taslak4.6 Excel'indeki üç biçim desteklenir: Ø20,5(M22x1,5-6H), Ø11,5(1/4"-18 NPT), Ø11,5(G1/4). Nominal geometri çapı ilk sayı olarak kalır; parantez içindeki tanım değiştirilmeden yerel threadCallout alanında saklanır. Metrik, G/R ailesi ve NPT için sınırlı tanıma grameri vardır; kapsam dışı veya bozuk biçimler sessizce çap sayılmaz, mevcut hata mekanizmasına düşer. Diş standardı/tablo uygunluğu veya üretim hesabı bu ayrıştırıcının doğruladığı bir şey değildir. Yazımın 6H/6h gibi harfleri değiştirilmez.

Etkin CAD isteğinde ForModel ayrı bir veri görünümü oluşturur: state, nominalMm, isZero, diameterSymbol. Diş çağrıları, ham metin ve toleranslar bu görünüme eklenmez. Yerel normalized-excel kaydı tam veriyi tutar. Eski sürüm geometride nominal kullanıyordu ama API tablosuna toleransı da gönderiyordu; bu değişiklikte tolerans artık API tablosundan da çıkarılmıştır. Geometri/ölçü sözleşmesi değiştirilmedi.

Python derleyici yerel hücre kaydını ölçünün sourceMeasurement alanına taşır. text_value, threadCallout varsa yalnız onu döndürür: M22x1,5-6H / 1/4"-18 NPT / G1/4. Ø20,5 veya Ø11,5 öne eklenmez. Normal hücrelerin çap/tolerans gösterimi korunur. Daha uzun metin mevcut etiket kutusu/çakışma hesabına otomatik girer; bu işlem bütün yerleşim sorunlarını çözmüş sayılmaz.

Yeni bir kozmetik diş çizgisi, helis, konik delik veya SolidWorks özelliği eklenmez. NPT hücresi de açık kullanıcı tercihi uyarınca verilen nominal silindirik geometriyle devam eder; parantez yalnız yerel ölçü çağrısıdır. STEP değişmez.

API çağrısı ve yeni ürün çizimi yapılmadı. Üç biçim için C# ayrıştırma, modele giden veride diş/tolerans alanlarının bulunmaması, v9 derleyicide çapın değişmemesi, yerel diş metninin anotasyona ulaşması test edildi. Gerçek taslak4.6 Excel'inin altı satırı (üç dişli/üç düz) da kontrol edildi. İki Python testi diş metninin nominali bastırdığını ve normal tolerans gösteriminin korunduğunu doğruladı.
