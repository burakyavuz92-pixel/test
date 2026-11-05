# Görünüş yerleşimi ve koordinat hatası teşhisi

## Uygulanan yerleşim değişikliği

Görünüş paketleri arasındaki tercih edilen boşluk 40'tan 120 sayfa pikseline çıkarıldı. Kullanılabilir alan darsa en az 40 piksel korunarak boşluk kısılabilir; bu tercih tek başına daha küçük ölçeğe zorlamaz. Yedi bospleyt paftasında kesit merkezi 40 piksel sola, ana/üst görünüş merkezi 40 piksel sağa taşındı (A5 üzerinde yaklaşık 4,8'er mm). Ölçekler değişmedi. Dört mevcut ölçek/yerleşim testi geçti; yedi gerçek paftada yön ve ölçek ayrıca kontrol edildi.

STEP dosyaları byte bazında aynı. part.py, measurements.py, measurement-references.json ve visual-markers.json değişmedi. Çözülemeyen 35 ölçü aynı kaldı; bu çalışma koordinat hatasını düzeltmiyor. API çağrısı yapılmadı.

## Hata hangi aşamada?

İlk çağrının geometri kodu doğru biçimde global Z ekseninde katı üretiyor. İkinci çağrının ölçü yanıtı, geometriyi tarif ederken kullanılan yerel profil koordinatlarını global/dünya koordinatları gibi döndürmüş.

Geometri kodu `cq.Plane(origin=(0,0,0), xDir=(1,0,0), normal=(0,-1,0))` tanımlıyor. Bu düzlemin yerel X yönü dünya X; yerel Y yönü dünya Z; yerel Z yönü dünya -Y. `.revolve(..., (0,1,0))` ekseni bu çalışma düzleminde tanımlanıyor. CadQuery'nin revolve uygulaması eksen noktalarını `self.plane.toWorldCoords(...)` ile dönüştürüyor. Böylece yerel `[0,1,0]` gerçek dünyada `[0,0,1]` oluyor. STEP silindir ve torus eksenlerinde bu sonuç ayrıca okundu.

İkinci model A için ekseni `[0,1,0]`, örnek merkezi `[0,-21,0]` vermiş. Bunlar profilin yerel çerçevesinde anlamlı; dünya çerçevesindeki karşılıkları `[0,0,1]` ve `[0,0,-21]`. Radyusların merkez/nokta/normal verileri ile J ve 3 uç noktalarında da aynı yerel-dünya çerçeve farkı var. Bu yüzden hata yalnız sayının veya tek bir noktanın yanlışlığı değil, ortak referans çerçevesi uyuşmazlığı.

## Sözleşmenin katkısı

İkinci çağrıya JPEG, nominal tablo ve geometri kodu metni gönderilmiş; gerçek STEP veya yürütülmüş düzlem/eksen özeti gönderilmemiş. Ölçü promptu 3B center/axis/points istiyor fakat bunların global/world koordinatlarında olmasını açık bir cümleyle tanımlamıyor. İlk geometri çağrısının +Z/orijin talimatları ikinci promptta aynen taşınmıyor. Modelin verilen koddan dönüşümü çıkarması mümkün; döndürdüğü verilerde ise dönüşüm uygulanmamış.

Doğrudan tespit: ikinci yanıt yerel çerçevede kalmış ve yürütücünün beklediği dünya çerçevesiyle uyuşmuyor. Açık dünya-koordinatı tanımının ve çalıştırılmış geometri çerçevesinin ikinci çağrıya aktarılmaması, sözleşme/tasarım eksikliği olarak görülüyor. Modelin iç muhakemesinde neden dönüşümü atladığı bu dış kayıtlarla kesin kanıtlanamaz.

İstenen doğrultuda prompt, sözleşme, model referansları veya koordinat dönüştürme koduna düzeltme uygulanmadı. coordinate-diagnosis.json yalnız teşhis kanıtıdır; üretim referans dosyası değildir.
