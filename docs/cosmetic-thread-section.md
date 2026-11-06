# @dis — yalnız kesitte sembolik gösterim

Mevcut genel @name yüzey etiketi kullanılır; prompta diş kuralı eklenmez.
STEP içindeki `dis` isimli silindirik yüzey okunur. Kesit düzlemi bu yüzeyi
boyuna kesiyorsa gerçek kesişim doğruları hesaplanır. Boy sınırları yüzeyin kendisinden
gelir; pah/konik geçişe taşınmaz. Kaçık kademeli kesitlerde gerçek bantla kırpılır.

Kesişimin iki tarafında, kesilen genişliğin %4'ü kadar içeriye ince paralel çizgiler;
iki uç sınırında eksene dik kesikli çizgiler çizilir. Bu bir diş standardı veya
imalat ölçüsü değildir; metin, adım ya da uygun çap hesabı yapılmaz.

STEP yüzey etiketi korunur; ek geometri üretilmez. Phong izometriye gösterim eklenmez.
`dis` etiketi olmayan veya ilgili yüzeyi kesmeyen kesitler ek çizgi almaz.
Şimdilik eksene paralel boyuna kesit gösterimidir; enine/eğik kesitlere halka veya
elips gösterimi eklenmez. İşaretlenen yüzey silindirik değilse hata raporlanır.
Pafta raporundaki cosmeticThread alanı çizilen bölge ve çizgi sayılarını kaydeder.

Testler: test_cosmetic_thread.py (tam boy, kaçık/dışarıda/teğet düzlem, etiketsiz
parça ve kademeli kesit bantları). Eş eksenli birden fazla ayrı silindir yüzeyi
seçimi mevcut yüzey eşleştirme kurallarıyla yapılır; bu özellik yüzeyi tahmin etmez.
