# Tek parametrik CadQuery betiği — taslak4

[Üç geometri önizlemesi](contact.jpg) · [JPEG ZIP](taslak4-script-3-jpeg.zip) · [Modelin değiştirilmemiş betiği](part.py)

## Uygulanan deney

C# ana uygulamaya analyze-script-group ve run-saved-script yolları eklendi. Eski JSON/pafta yolu silinmedi; bu ayrı bir geometri deneyi. Model yalnız build_part(p) fonksiyonu üretiyor. Bir satırın nominal değerleri p üzerinden veriliyor; STEP ve önizlemeyi yerel yazılım oluşturuyor. Kesit, antet, ölçülendirme, detay/pafta verisi istenmedi. Bu, bütün üretim paftası işinin tamamlandığı anlamına gelmez.

Aynı taslak4 JPEG ve Excel kullanıldı; kaynak özetleri önceki group4-gemini-high-axis ile aynı. Excel yerelde ayrıştırıldı; nominal sayılar modele gitti, toleranslar normalized-excel.json içinde yerelde korundu. Kaynak dosyalar ve model yanıtı değiştirilmedi. Modele F'nin içe çökmesi hakkında ek açıklama gönderilmedi.

Model google/gemini-4-argon ve high sabit tutuldu. Tek API çağrısı. Çıktı modeli p[A..J] kullanan tek fonksiyon; satır numarası/ürün başına betik yok. Yerel runner fonksiyonu her satır için çağırıyor. Standart Python aritmetiği kullanılıyor, özel JSON parametre/işlem diline çevrilmiyor.

## Ortam ve çalıştırma

CadQuery2.6.1 ayrı /workspace/cq-venv ortamına kuruldu; eski OCCT ortamı değiştirilmedi. Kilitli paket listesi tools/cadquery-script-requirements.lock. CadQuery de OCCT kullanıyor; yerelde CPU. Yeni ortam OCP7.8, mevcut önizleme ortamı farklı sürüm olduğu için geometri STL üzerinden mevcut CPU mesh görüntüleyicisine aktarılıyor. STEP yeniden okuma yeni ortamda yapılıyor.

Generated kaynak AST ile sınırlanıyor: yalnız cadquery/math importu, build_part ve yardımcı fonksiyonlar; dosya/export/ağ/modül erişimi isimleri engelleniyor. Çalışırken Python IO audit kontrolü, anahtarların süreçten çıkarılması, CPU/dosya boyutu ve süreç süre sınırı var. Bu kontroller genel amaçlı, tam bir OS sandbox garantisi değildir. Buluttaki bwrap kullanıcı alanı izinleri nedeniyle ek sandbox kurulamadı; bunun var olduğu iddia edilmedi. Dışarı giden tek ücretli model çağrısı C# analizinden yapıldı.

## Sonuç

Üç gerçek satır için tek pozitif hacimli geçerli katı, STEP ve iki açıdan geometri JPEG'i üretildi. STEP yeniden okuma/hacim tutarlılığı geçti. Kod elle onarılmadı.

R8/R5/R1.5 ana gövde profili yaylarla tarif edilmiş; G ve I y=±C/2, manşon x=−B. B0 ürününde merkezdeki manşon korunuyor. F yine z_start=−F olarak kullanılmış: kullanıcının istediği içe0.5 çökertme yerine dışarı taşma. Betik arka tarafta r_flange=D/2+1.5 ek flanş da seçmiş. Bu geometri yorumları kullanıcının gerçek parçası olarak kabul edilmedi. Geçerli BRep, doğru parça demek değildir.

## 80 satır testi

Aynı değiştirilmemiş betik, üç gerçek satırın tekrarından oluşan80 sentetik kayıtla yerelde çalıştırıldı.80 katı geçerli; aynı script SHA256. Bu yük/yeniden kullanım testidir,80 farklı ölçü kombinasyonunun doğruluk testi değildir. STEP/JPEG80 kez dışa aktarılmadı; katı oluşturma/geçerlilik kontrolü yapıldı. API çağrısı0. Sonuç80-row-local-check.json içinde.

5 yeni yerel test ayrıca basit parametrik fonksiyonun80 farklı çapla çalışmasını ve yasak import/dosya/export/top-level işlemlerin reddini kontrol ediyor. Mevcut77 C# kontrolü geçti. Bunlar modelin geometri yorumunun doğruluğunu kanıtlamaz.

## Kullanım karşılaştırması

|Metrik|Önceki JSON + pafta, high|Betik + yalnız geometri, high|
|---|---:|---:|
|Giriş token|3956|1608|
|Akıl yürütme|15328|11131|
|Görünür çıktı|2557|1568|
|Toplam çıktı|17885|12699|
|Maliyet USD|0.186762|0.130206|

Cache0. Giriş yaklaşık%59, akıl yürütme%27, görünür çıktı%39, maliyet%30 azaldı. Fakat format ve görev kapsamı birlikte değişti; düşüşü yalnız betik diline bağlayamayız. Birden çok çalışma/statistik yapılmadı. 0.130206 USD hâlâ az bir ilk analiz ücreti sayılmayabilir ve F yönü yanlış. Yeni yaklaşım geometri doğruluğunu kendi başına çözmedi.

Betik3530 karakter; grup için tek kez üretildi.80 satır,80 betik anlamına gelmiyor. Artan yük yerel katı oluşturma süresinde. Onaylı script kitaplığı ve tam teknik pafta bağlantısı henüz bu deney yoluna entegre edilmedi; eski JSON kitaplığı bundan ayrı. Bu aday kullanıcı onaylı üretim betiği olarak işaretlenmedi.
