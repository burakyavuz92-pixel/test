# Aynı notsuz girdi ve sade prompt: high akıl yürütme denemesi

Kullanıcı isteğiyle kırmızı notları önceden silinmiş taslak2guncel-notesiz.jpg ve taslak2guncel.xlsx (4 satır) yazılıma gönderildi. Özgün notlu resim kullanılmadı. Ürün çizimi oluşturulmadı.

## Karşılaştırmanın denetimi

Önceki low başarısızlığıyla gerçek gönderilmiş request-prompt.txt, model-input.json, geometry-input.json ve geometry-no-red.jpg SHA256 özetleri birebir eşleşiyor. Aynı model ve max_tokens=6000 kullanıldı; yeni çağrıda istenen tek ayar farkı reasoning.effort=high. Önceden var olan normal üretim promptu ve low varsayılanı değiştirilmedi. Program analiz komutuna açık --reasoning=low|medium|high seçeneği eklendi; bu deneme --technical-jargon --reasoning=high ile yapıldı. Model metadata'sında reasoning desteklenen parametreler arasında görüldü. Değiştirilen kod parçaları yalnızca ayar seçimi, doğrulaması ve kayıt altına alınmasıdır.

Yanıt JSON kod bloğu içinde geldi; mevcut ExtractJson bunu ayrıştırdı. JSON içeriği özgün API content'iyle semantik olarak aynı, model planı elle değiştirilmedi. Gizli akıl yürütme metni yayımlanmıyor; yalnızca sağlayıcının token sayaçları paylaşılır.

## Sonuç

Model orijini gövde ana ekseninde seçti. Üst delik X=0 ve Y=altY+B, alt delik X=0 ve Y=-G, üçüncü delik X=-F/Y=0. E boş olduğunda üçüncü delik yok; sıfır F gerçek merkez konumu. B üst-alt merkez mesafesi, F orijin-E yatay kaçıklığı, G orijin-D dikey kaçıklığı olarak tutarlı eşleşti. B/G için simetriye zorlamadı.

| Ürün | Üst Y | Alt Y | Üçüncü delik |
|---|---:|---:|---|
| 11-30-212 | 44,45 | -44,45 | (-44,5; 0) |
| 11-30-200 | 44,5 | -44,5 | Yok |
| 11-30-92 | 86,7 | -78,7 | Yok |
| 11-30-381 | 35 | -35 | (0; 0) |

F için hideIf=zero ve G için hideIf=equalsScaledColumn(B,0.5) döndü; D çapı gereksiz yere gizlenmedi. Kesit hedeflerinde üç delik var. Yeşil sabitlerin modeldeki visible=true bayrakları yerel renk politikasıyla gizleniyor ve bu durum uyarı olarak kaydediliyor; geometri değişmiyor. Durum analysis-only, bloklayıcı hata yok. Bunlar native çizim üretimi veya bütün görsel yerleşimlerin onayı anlamına gelmez.

## Token ve maliyet

| Ayar | Input | Completion (reasoning dâhil) | Reasoning alt sayacı | USD |
|---|---:|---:|---:|---:|
| Önceki low | 14889 | 2102 | 0 | 0,050798 |
| Yeni high | 14889 | 4793 | 2264 | 0,077708 |

Reasoning sayacı completion toplamına dâhildir; tekrar eklenmez. Bu görevde yalnızca bir yeni model çağrısı yapıldı, 0,077708 USD. Her iki kayıtta cache okuma/yazma sıfır. Sağlayıcının sayaçları high çağrısında ek muhakeme kullanıldığını gösteriyor; tek karşılaştırma istatistiksel güvenilirlik veya bütün taslaklarda başarı kanıtı değildir.

77 C# kontrolü geçti. Yeni çizim yok. AssistantAnswersUsed=false. Parametre ve girdi eşitliği kanıtları comparison.json içinde.

## Sonraki adım

Bu başarılı analizi aynı ayarla tekrarlayarak dayanıklılığı sınamak veya değiştirilmemiş planla yeni API çağrısı olmadan çizim denemek mümkün. Bu görevde ikisi de yapılmadı. Üretimin varsayılan modeli/promptu/effort ayarı değiştirilmedi.
