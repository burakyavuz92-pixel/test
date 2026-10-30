# DrawingTool — genel CAD tarifi v6

Girdi JPEG + Excel. Model parçayı genel bir parametre/işlem tarifiyle tanımlar; ölçüler ve kesitler aynı işlem kimliklerine bağlıdır. Eski pleyt/Skia kökenli tarif ve v4 adaptörü aktif akıştan kaldırılmıştır; archive/legacy-v4 geri izleme içindir.

**Mevcut aşama:** tek API analizi, parametre/işlem bağımlılıklarının doğrulanması ve her Excel satırı için çözümlenmiş JSON üretimi. Genel işlem listesini OCCT katısına ve teknik paftaya dönüştüren yeni yürütücü henüz uygulanmamıştır. Bu sürüm eski 82-pleyt üretimini yeniden çalıştırmaz. Eski native deney experiments/occt altında kalır, v5 CLI onu çağırmaz. Bir tarifin doğrulanması gerçek katının üretildiği veya JPEG'in doğru olduğu anlamına gelmez.

## Kullanım

```bash
dotnet run --project src/DrawingTool.csproj -- analyze-cad-group input.xlsx template.jpg output/empty-run
```

Varsayılan sade teknik resim yorumu, high akıl yürütme, tek API çağrısı. max_tokens=20000 üst sınırdır, her çağrıda bu kadar harcanmaz. Otomatik yeniden değerlendirme yok. Eksik yanıt, eksik parametre, bilinmeyen işlem veya çelişki raporlanır. Kaynak SHA256 özetleri ve özgün yanıt saklanır. API anahtarı/Arial fontu repoya konmaz. Model analizi OpenRouter üzerinden, çözümleme yereldir.

`run-cad-group` aynı güncel analizden sonra genel native yürütücünün eksikliğini raporlar; sessizce eski pleyt motoruna dönmez. Eski run-cad/render-cad-plan/occt-demo komutları kaldırılmıştır. Tarihsel çıktılar previews altında korunmuştur.

## Sözleşme

- parameters: Excel nominali, sabit sayı veya iki parametreye bağlı add/subtract/multiply/divide. mm/deg/count/scalar birim kontrolleri; döngü/sıfıra bölme kontrolü. Toleranslar kaynak Excel'de ayrıca korunur.
- frames: origin, xAxis/zAxis ve görsel kanıt. Bazlar normal ve dik olmalı.
- operations: sketch, extrude, revolve, cylinder, cut, fuse, hole, circularPattern, linearPattern, fillet/chamfer. Bu liste **tarif sözcük dağarcığıdır**, yeni native uygulamanın tamamlandığı anlamına gelmez. İşlem args doğrulaması temel alan/girdi/dependency kontrolüdür; bütün geometrik ayrıntıları doğrulamaz.
- inputs/optionalInputs/when: bağımlılık, isteğe bağlı özellikler ve sıfır yüksekliğe bağlı topoloji değişimi.
- dimensions: parametre ve semantik operasyon/yüz/eksen hedefleri, adet, renk ve gösterim koşulu. Yeşilin effectiveVisible değeri yerelde false yapılır; kaynak plan değiştirilmez.
- views/sections/geometricTolerances: aynı özellik kimliklerine bağlı sunum tarifi. Semantik yüz hedeflerinin gerçek OCCT yüzleriyle eşleştirilmesi henüz tamamlanmadı.

Katı oluşturma, ölçü ilişkilerinin genel geometrik çözümü, native topoloji eşlemesi ve genel pafta yerleşimi sonraki geliştirmelerdir. Modelin tarifi doğru anlaması bağımsız görsel doğrulamayla garanti edilmez.

## Kurulum ve kontrol

.NET SDK global.json ile sabitlenir, ClosedXML NuGet paketidir. OPENROUTER_API_KEY ve OPENROUTER_MODEL ortamda tanımlanmalı. Analiz ön işleme için Python/Pillow gerekir (OCCT_PYTHON seçilebilir; bulutta /workspace/occt-venv/bin/python). Yeni paket eklenmedi.

```bash
dotnet build src/DrawingTool.csproj
dotnet run --project checks/LayoutPolicyChecks.csproj
```

Eski testler arşivdedir; güncel testler yeni tarif çözümleyicisine aittir. Başarılı testler native CAD çıktısı üretildiği anlamına gelmez.

## v6: tek hedef ve koşullu gövde akışı

Aktif tarif sürümü 6'dır. hole/fillet/chamfer tek `target`, cut tek `target` ve `tool` kullanır; bu işlemlerde inputs/optionalInputs boş olmalıdır. Koşul false ise etkin gövde sonucu target'ın aynısıdır, çözümlenmiş planda passThrough kaydı oluşturulur; boş özellik parametreleri bağlanmaz. `featureApplied=false` ayrı tutulur: gövdenin mevcut olması deliğin/özelliğin oluştuğu anlamına gelmez. Atlanan özelliğin ölçüleri ve kesit hedefleri çıkarılır. Oluşturma işlemlerinde false koşul hâlâ hiç şekil üretmemek demektir; fuse yalnız kendi optionalInputs kayıtlarını atlayabilir. Eski alternatif-gövde-listesi semantiği kabul edilmez. Sürüm 5 kayıtları otomatik dönüştürülmez. v6 da hâlâ tarif/çözümleme aşamasındadır; genel native yürütücü tamamlanmadı.

26 tarif kontrolü geçti. Aynı notsuz taslak2guncel JPEG ve Excel'in v6 analizi previews/group2-v6-analysis/NOTLAR.md içinde. Koşullu zincir geçti, ancak modelin R8'i iç yarıçap kabul etmesi ayrıca incelenmeli; biçim doğrulamasının geçmesi bütün geometri yorumunun onayı değildir.
