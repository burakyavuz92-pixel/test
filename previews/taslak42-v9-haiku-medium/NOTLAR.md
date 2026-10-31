# Taslak4.2 — Haiku 5.5 / medium

Model anthropic/claude-haiku-5.5; provider=Claude Platform on AWS. Aynı orijinal JPEG, Excel, tam metin girdisi ve sözleşme kullanıldı. Görsel küçültülmedi. Önceki high ile aynı 32768 completion sınırı. Bu denemede OPENROUTER_REASONING_EFFORT=medium gönderildi; rapor aynı değeri kaydediyor. Tek API çağrısı; geometri/sözleşme değiştirilmedi, model çıktısı elle düzeltilmedi.

| Ölçüm | Haiku high | Haiku medium |
|---|---:|---:|
| Input token | 9825 | 9825 |
| Reasoning token | 31559 | 18020 |
| Görünür completion (toplam−reasoning) | 1209 | 2538 |
| Toplam completion | 32768 | 20558 |
| USD | 0,0173665 | 0,0112615 |
| finish_reason | length | stop |

API yanıt dosyasına kadar yaklaşık 106 saniye; high yaklaşık 161 saniyeydi. Bunlar salt düşünme süreleri değil. Medium maliyeti yaklaşık %35,2, reasoning sayısını %42,9 azalttı. Cache 0. Bunlar tekil denemelerdir.

## Neden çizim oluşmadı?

Bu kez token sınırına takılmadı; model stop ile bitirdi. Ancak görünen yanıttaki JSON geçersiz. İlk geometri özelliğinde profilin ardından fazla kapanış parantezi var; C# ve bağımsız Python json.loads aynı yerde (857 sıfır tabanlı karakter konumu) hata verdi. Kod bloğu sarmalayıcısını çıkarmak sorunu gidermiyor. Uygulama JSON modu istemesine rağmen geçerli JSON gelmedi. Ham yanıt invalid-response.txt içinde, onarılmadan korunmuştur. Gizli reasoning metni yayımlanmadı.

Yerel CAD aşaması başlamadı; STEP/JPEG yok. Sözdizimi elle düzeltilmedi, geometriyi kurtarma veya yeniden API çağrısı yapılmadı.

## Görünen metinden gözlemler

Kap gövdesi revolve, ilgili bölge J+6, 2 mm fillet ve G/I delikleri olarak tarif edilmiş. F ise pad/add silindirini z=-F'den başlatan dışa çıkıntı şeklinde. Dolayısıyla daha az reasoning yeterli/doğru sonucu sağlamış değil. Ayrıca profil son noktasından başlangıca kapanan son segment görünür listede eksik; JSON onarılsa bile bütün tarifin geçerli olduğu söylenemez. A ölçüsü de yeşil işaretlenmiş. Bu gözlemler yürütülmüş geometri sonucu değildir.

## Yazılım değişikliği

Hard-coded high yerine OPENROUTER_REASONING_EFFORT ayarı eklendi; unset ise high kalır. Bu çalışmanın süreç ayarı medium idi; global varsayılan düşürülmedi. Desteklenen standart effort sözcükleri yerelde doğrulanır; seçilen modelin her effort düzeyini desteklediği varsayılmaz. 91 mevcut C# kontrolü ve derleme geçti. Prompt ve geometri yürütücüsünde değişiklik yok.

Bir sonraki deney yapılmadı. Bu sonucu başarılı saymıyoruz. Sırf reasoning azalması yeterli değil; geçerli ve taslakla eşleşen tamamlanmış tarif gerekli.
