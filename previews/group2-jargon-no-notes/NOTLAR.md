# Sade teknik yorumlama talimatı — kırmızı notsuz analiz

Bu deneme, kullanıcının koordinat girişi yerine teknik resmi modelin anlamaya devam etmesi isteğiyle yapıldı. Güncel taslak2guncel.xlsx dört satırı ve taslak2guncel JPEG temel alındı.

## Girdi ve düzeltme

İlk istekle sade prompt/notlu JPEG çağrısı başlamıştı. Kullanıcı kırmızı notların kaldırılmasını istediğinde bu çağrı tamamlanmıştı; iptal edilmedi. O sonuç notlu ön deneme olarak ayrı kaldı.

Özgün JPEG değiştirilmedi. İki kırmızı talimat kutusu ve kutu çerçeveleri kopyada beyazlandı. Alanlar input-cleanup.json içinde; bu koordinatlar yalnızca mevcut girdideki iki notun temizlenmesi içindir, CAD yorumlayıcıya gömülü parça konumu değildir. Ölçü harfleri, siyah/yeşil ölçüler, kesit izi ve görünüşler korunarak kopya görsel açılıp kontrol edildi. JPEG yeniden sıkıştırma kenar piksellerinde küçük değişiklik yapabilir. Notsuz gerçek girdi input-without-notes.jpg olarak saklandı. Antet/logodaki kırmızı baskılar korunmuştur; kaldırılanlar yalnızca iki talimat kutusudur.

Sade prompt ile bu notsuz kopya ve aynı Excel yazılımın analyze-cad-group yolunda gönderildi. Tek yeni çağrı, otomatik ikinci değerlendirme yok, çizim yok. Modelin planı elle değiştirilmedi.

## Prompt değişikliği

Yorumlama talimatı genel teknik resim kuralları, jargon, eksenler/kesitler/görünüşleri birlikte okuma ve açık bilginin önceliği şeklinde kısaltıldı. "Simetri varsayma", belirli yarım-mesafe örnekleri ve delik yerleşimine yönelik özel yönlendirmeler çıkarıldı. Orijin, birimler, JSON alanları, nominal/tolerans ayrımı ve yerel yazılımın destek sınırları korundu. Promptta B-G/-G/-F gibi bu grubun doğru cevabı yok.

## Notsuz sonucun değerlendirmesi

Orijin gövde ana ekseninde doğru seçildi. Alt delik Y=-G ve üçüncü delik X=-F/Y=0 doğru. Boş E/F ve sıfır F ayrımı korunmuş. Ancak üst delik Y=+G yapıldı; model üst/alt deliklerin simetrik olduğu sonucuna vardı. Özgün yanıtta B'nin üst-alt mesafesi olduğu yazmasına rağmen geometri 2G mesafesi üretmiş.

| Ürün | Model üst Y | Gerekli üst Y | Alt Y | Sonuç |
|---|---:|---:|---:|---|
| 11-30-212 | 44,45 | 44,45 | -44,45 | Bu satırda sayısal olarak uyumlu |
| 11-30-200 | 44,5 | 44,5 | -44,5 | Bu satırda sayısal olarak uyumlu |
| 11-30-92 | 78,7 | 86,7 | -78,7 | Üst delik 8 mm yanlış |
| 11-30-381 | 35 | 35 | -35 | Bu satırda sayısal olarak uyumlu |

92 için modelin merkezler arası mesafesi 157,4; Excel B=165,4. Yazılım bunu yakalayıp blocked-with-report durumunda durdu. Doğru Excel'i değiştirmek gerekmiyor. Modelin "B/G tutarsız" açıklaması doğrulanmış girdi hatası değil, yanlış simetri kabulünün sonucu.

F/G measurementSources uç kayıtları da mevcut annotation sözleşmesiyle eşleşmedi. Bu kayıtlar sırasıyla E-C ve E-D merkezlerini verirken annotation origin-relative offset istiyor. Bazı projeksiyonlar ortak eksen üzerinde eşdeğer olabilir; mevcut sözleşme bunu genel olarak çözmüyor. Üst deliğin 8 mm hatası bundan bağımsız, açık sayısal bir geometri hatasıdır.

Gösterim tarafında G için hideIf=never, D için C ile eşitse gizle kuralı döndü. Kırmızı notların eski gösterim tercihlerinin notsuz girdiden aynen çıkarıldığı söylenemez. Bunlar çizilmedi.

## Maliyet ve kontroller

Notsuz esas deneme: 14.889 input, 2.102 output, 0,050798 USD. Önce tamamlanmış notlu deneme: 14.889 input, 2.033 output, 0,050108 USD. Bu görevde iki çağrının toplamı 0,100906 USD. Cache okuma/yazma her ikisinde 0. Yeni JPEG teknik çizimi 0, model planı düzeltmesi 0.

77 C# kontrolü geçti. Bu kontroller JSON/çözücü sözleşmesini doğrular; modelin görsel yorumunun doğru olduğunu kanıtlamaz.

## Üretim sürümünün korunması

Yeni sade prompt beklenen sonucu vermediğinden varsayılan üretim promptu olarak etkinleştirilmedi. Son başarılı üretim talimatları CadAnalysisPrompt.Instructions içinde korundu. Sade sürüm TechnicalJargonDraft olarak ayrı tutulur; yeniden deneme için:

```
dotnet run --project src/DrawingTool.csproj -- analyze-cad-group <xlsx> <jpeg> <empty-output> --technical-jargon
```

Normal run-cad-group değişmeyen üretim promptunu kullanır. Bu iki gerçek çağrı, kodda ayrım yapılmadan önce sade sürümle çalışmıştı; sonradan ayrım eklenmesi yeni API çağrısı üretmedi. Ham istek/yanıtlar yerelde korunur.

Bu deneme sadeleştirmenin bütün modellerde başarısız olacağını veya mutlaka özel B/G kuralları gerektiğini kanıtlamaz. Mevcut model/ayar/görsel için genel yorumlama talimatı tek başına asimetrik satırdaki doğru ilişkiyi çıkarmadı.
