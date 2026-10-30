# Genel CAD veri sözleşmesi ve yürütücü incelemesi

API çağrısı, çizim veya uygulama kodu değişikliği yapılmadı. Kaynaklar CadAnalysisPrompt, CadPlanV3, CadGroupExecutor, CadReferenceFrame, OcctProcessBackend ve Python worker/technical_sheet.

## Mevcut yol ve sınırlar

1. Model v4 JSON: coordinateFrame, tek geometry.kind, holes, annotations, section, camera.
2. CadPlanV3.Bind Excel'e göre konumları çözer; v4'ü eski v2 planına indirger. Geometride yalnız origin/offset ve ±sütun adımı var; genel katsayı veya profil yok.
3. CadGroupExecutor.Resolve yalnız kind=revolved-plate kabul eder; dış çap/depth/thickness/radius ve delikleri sayısallaştırır. depth/thickness/radius kaynak planda sabit sayıdır; genel Excel parametresi değildir.
4. Python worker her zaman aynı yuvarlatılmış çanak kesitini oluşturup döndürür, delikleri keser. depth>radius>thickness koşulu gövde ailesine özeldir.
5. technical_sheet görünüşleri aynı katıdan çıkarır ama pafta yerleşimi elle kalibredir; çap ölçüsü body veya hole bekler. Kalınlık/yüzey mesafesi/hatve dairesi/grup ölçü türleri genel olarak yok.

Ortak altyapı kullanılabilir: Excel ayrıştırma ve toleranslar, yerel renk politikası, Arial metrikleri/etiket çakışma kontrolü, süreç izolasyonu, OCCT boolean/HLR/section/CPU render/STEP doğrulamaları, kaynak bağlama ve raporlar. Değişmesi gereken bu altyapının hepsi değil, geometri tarifi/yürütücü ve özellikten ölçüye bağlantı katmanıdır.

## Önerilen yeni sözleşme

- parameters: bütün değişken boyutlar Excel sütununa, sabitler değere bağlı; nominal ve tolerans gösterimleri ayrı. Kapalı, birim denetimli sayı ifadeleri (column/constant/add/subtract/multiply/divide), model kodu çalıştırılmaz.
- frames/datums: mevcut ortak referans sözleşmesinin kontrollü genişletilmesi.
- features/operations: mantıksal ID, kaynak geometrisi, parametre bağları, koşul ve bağımlılık. Başlangıç katalogu: kapalı çizgi/yay/daire profili; extrude/revolve; union/cut; through/blind cylindrical hole; circular/linear pattern; kontrollü fillet/chamfer. Her işlemin kodu, doğrulaması ve raporu birlikte yazılmalı. Bütün CAD işlemlerini ilk sürümde desteklemek gerçekçi değil.
- dimensional relations: ölçülen özellikler/eksen/yön/parametre bir kez tanımlanır. Koordinatlar bu ilişkilerden türetilir. Tam genel 3D kısıt çözücüsü yerine ilk kapsam açıkça sınırlanabilir; çözülmeyen/döngüsel/eksik kısıtlar tahmin edilmez.
- annotations: ortak ilişkiye referans; tolerans kaynağı, adet, görünüş, tercih edilen gösterim yönü, yerel gizleme koşulu. Aynı ölçünün ikinci kez bağımsız geometrik yorumu yok.
- views/sections: görünüş doğrultusu, kesit amacı ve özellik hedefleri; pafta bölgeleri ve görünüş yerleşimi gövdeden ayrı.
- evidence/issues: modelin kaynak yorumu ile yerel destek/doğrulama sonuçları ayrı tutulur.

Görsel modeli parça ve ölçü bağlantılarını çıkarır; kullanıcı yalnız JPEG/Excel verir. Yerel kod tanımlanan genel işlemleri uygular, geometrik hesabı yapar. Bu, parçayı kullanıcıya yeniden çizdirmek değildir. Modelin doğru gözlemleri hâlâ gereklidir, yeni şema yorum hatalarını otomatik yok etmez.

## Kapak örneğinin karşılığı

| Taslaktaki özellik | Genel tarif |
|---|---|
| Dış gövde A, levha kalınlığı F | Dairesel profil + kalınlık verme |
| Merkez delik D | Eksenel kesme |
| 4×C, B hatve çapı | Silindirik delik + B/2 yarıçaplı circular pattern |
| İki açık kenar çentiği | Yuvarlak uçlu profil kesme + karşılıklı çoğaltma |
| Delik çevresi kabartı | Ek profil/katı birleştirme, boyut ve geçişler yeterliyse |
| Ölçü B, 4×C, E/F | Construction circle/grup ölçüsü/yüzeyler arası lineer ölçü |

Bu yalnız eşleştirme örneğidir, üretim planı değildir. Çentik açısı veya kabartı çapı/yarıçapı kesin ölçülü değilse model bunları hassas imalat boyutu olarak uydurmamalı. Kullanıcının ölçüsüz görsel detayda yaklaşık temsile izin verdiği durumlar açık kalite kaydıyla ayrılabilir. E/F nominal eşitliği, kabartının sıfıra inmesini gerektiriyorsa yerel sıfır-özellik davranışı test edilmeli; otomatik olarak girdi hatası sayılmamalı.

## Referans ve doğrulama tasarımı

Üretilmiş OCCT yüz sırasına (örneğin face7) bağlanmak kararlı değildir; boyut ve boolean değişimlerinde sıralar değişebilir. base.frontFace, hole1.axis, pattern1.instances gibi anlamsal hedefler ve bunları native sonuçlarla ilişkilendiren provenance/selector katmanı gerekir. Bu eşleştirme başlı başına CAD geliştirme işidir.

Doğrulama: şema ve alan türleri, desteklenen işlemler, birim/pozitiflik, bağımlılık ve eksik parametreler, ölçü ilişkileri, katı geçerliliği/özellik varlığı, görünüş ve yazı yerleşimi. Boş girdide koşullu özelliğin yokluğu ile 0 konumun varlığı korunur. STEP hacim kontrolü tek başına taslağın doğru okunduğunu kanıtlamaz. Başarısız işlem atlanıp tamamlanmış resim gibi sunulmaz.

Sağlayıcı desteği doğrulanarak sıkı JSON Schema çıktısı kullanılabilir; yalnız json_object biçimi alan adlarını garantilemiyor. Bu biçim hatalarını azaltır, yanlış ölçü ilişkisini çözmez. Prompt teknik resim yorumunda kısa, veri sözleşmesinde açık olmalı. İşlem katalogu sınırlı ve sürümlü tutulursa token yükü yönetilebilir; yeni aile başına bütün kuralları prompta eklememek gerekir.

## Aşamalı öneri

1. Genel sözleşmenin örneğini bu kapağa göre hazırlamak; önce yeni sade yorumlama + high ile çizimsiz analiz. Mevcut pleyt kind şemasını zorlamamak.
2. Modelin tanıma çıktısını değerlendirmek. Yeni parça üzerinde doğru tanıma henüz test edilmediğinden peşinen garanti verilmez.
3. Gerekli ortak operasyonların yürütücüsünü ve genel ölçü bağlantılarını tamamlamak. Kapağa özel sabit çizim kodu yazmamak.
4. Hem eski pleyt grubu hem üç kapak satırı ile doğrulamak; eski 82 çıktılık başarıyı gerileme kontrolü olarak korumak.
5. Yeni yol kanıtlanana kadar mevcut çalışan v4 adaptörünü ayrı tutmak; yeni şema üzerinden yerleşim/kesit kapsamını aşama aşama genişletmek.

Önce yalnız geometriyi genelleyip ölçülendirmeyi eski sabit profile bırakmak yeterli değildir. JPEG teknik doküman olduğundan bu iki iş paralel tasarlanmalı. Bu metin plan/incelemedir; önerilen genel motor şu anda uygulanmış değildir.
