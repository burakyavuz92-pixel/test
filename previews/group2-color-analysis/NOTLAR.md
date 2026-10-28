# Renk ayrımıyla çizimsiz analiz

Dosyalar ortamda taslak2guncel.xlsx ve taslak2guncel.jpg adlarıyla bulundu. Kullanıcının son mesajındaki taslakguncel2 adları bunlara referans olarak alındı. Excel dört satır içeriyor. Kaynak SHA256 özetleri api-run-report.json içinde. Girdiler değiştirilmedi.

## Düzenleme

- Tek API çağrısında geometri için kırmızı pikselleri çıkarılmış görüntü, gösterim için özgün renkli görüntü verildi. Yerelde 67.741 kırmızı piksel beyazlandı; siyah/yeşil pikseller korundu, görüntü boyutu değiştirilmedi. Bu ürün çizimi değildir, girdi ön işleme görünümüdür. Renk eşikleri soluk kırmızı kalıntılarını kaçırabilir.
- Geometri yükünde nominal, boş/sıfır ve çap bilgisi var, tolerans alanı yok. Ölçülendirme yükünde tolerans sapmaları ayrı alanlarda var. Model her iki yükü aynı çağrıda görebilir; bu bağımsız iki analiz değildir.
- Kırmızı notlar yalnızca görünürlük, yeşil ölçüler geometri fakat gizli gösterim, siyah ölçüler normal geometri/gösterim olarak tanımlandı. Gizleme koşulu, varlık ve kesit hedefleri ayrı tutuldu. Eşitlikler nominal değerlerde; tolerans aralığı çakışması eşitlik sayılmaz.
- Çıktıya measurementSources ile sütun, renk, eksen ve ölçü uçları; sabit ölçülere sourceColor eklendi. Renk kaynak iddialarının geçerliliği ve yeşilin gizlenmesi denetlenir. Denetimler modelin kendi bildirdiği renk/özellik eşleşmesine dayanır; bağımsız görsel doğrulama değildir.
- analyze-cad-group komutu çizim motorunu çağırmadan durur. Otomatik ikinci API çağrısı yok.

## Gerçek sonuç

API çağrısı 1; sağlayıcının bildirdiği maliyet 0,050022 USD. JPEG çizimi 0. Model planına elle müdahale 0. Aynı yanıt yeni API çağrısı yapılmadan güçlendirilmiş yerel denetimle tekrar incelendi.

Doğru dönenler: R8/33/3 yeşil sabitleri geometride korudu, gösterimlerini gizledi; F=0 ve G=B/2 gizleme kurallarını yalnızca annotations bölümüne yazdı; kesit hedeflerine üç deliği dâhil etti; boş E için isteğe bağlı delik varlığını tanımladı.

Yanlış dönenler: E deliğini ana orijin yaptı. C ve D'nin yatay konumunu F ile E deliğine bağladı. C yüksekliğini B, D konumunu C-G olarak kurdu. B'yi üst-alt delik merkez mesafesi yerine üst deliğin orijine uzaklığı gibi tanımladı. F'nin ölçü hedefini üçüncü delik yerine üst deliğe bağladı. E olmayan iki satırda C ve D olmayan bir özelliğe bağlı kaldı. Bu, Excel ayrıştırma veya tolerans sayısının bozulması değil, çizimdeki referans ve ölçü uçlarının yanlış eşleşmesidir.

Yerel ek denetim, measurementSources uçları ile annotations uçlarının çelişkisini B/F/G için yakaladı. Örneğin G kaynak kaydı C-D derken ölçü türü origin-D uzaklığı istiyor. Sayısal değer tesadüfen tutsa bile bu çelişki reddediliyor. Aynı tutarsızlık kontrolü farklı sütun adları için de çalışır; B/F/G için doğru geometri yazılıma gömülmedi.

## Kontroller ve sınırlar

63 C# kontrolü ve kırmızı çıkarma/siyah-yeşil koruma testi geçti. Bu görevde OCCT yürütülmedi; çizim üretilmedi. Ürün geometrisini veya kesit motorunu değiştirip denemedik. Runtime'daki renk protokolü yeni grup yollarına uygulandı; tarihsel v1 tek-ürün API yolu aynı çift-görüntü protokolünü kullanmıyor.

Renk ayrımı bu denemede gösterim ve kesit hedeflerinde iyileşme sağladı, fakat tek deneme nedensellik kanıtı değildir. B/F/G geometri bağlantılarını çözmedi. Sonuç blocked-with-report. Doğru Excel'e değer eklemek veya değer değiştirmek önerilmiyor.

## Sonraki adım önerisi

Ana sorun olarak kalan ölçü ucu/ana eksen tanımayı ele almak: özgün şema üzerinde ölçü bölgelerinin okunabilirliğini yakın görüntülerle değerlendirmek veya aynı sabit girdilerle kontrollü model karşılaştırması yapmak. Bunlar bu görevde çağrılmadı. Önce bu yanıtın hataları üzerinden yöntemi seçmek gerekir; bugün özerk üretim başarısı iddiası yok.
