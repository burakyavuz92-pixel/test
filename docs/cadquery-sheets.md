# CadQuery gövdesini mevcut pafta hattına bağlama

Geometri doğrulanıp `rows.json` ve her ürünün `<id>/<id>.step` dosyaları oluşturulduktan sonra depo kökünden:

```bash
OCCT_PYTHON=/workspace/occt-venv/bin/python \
DOTNET_CLI_HOME=/workspace/.dotnet-home NUGET_PACKAGES=/workspace/.nuget/packages \
/workspace/.dotnet/dotnet run --project src/DrawingTool.csproj -- \
  render-script-sheets input.xlsx template.jpg output/saved-script
```

API çağrısı yapmaz. Excel parametrelerinin kayıtlı script parametreleriyle eşit olması gerekir. Yerel kamera/kesit ayarlarını C# ayrıştırır; nominal ve toleranslar mevcut Excel ayrıştırıcısından gelir. STEP, mevcut OCCT pafta motoruna verilir. Antet, OCR etiketi, kesit, sayısal ölçek, JPEG ve PDF aynı hattı kullanır. Bu komut ilgili ürün JPEG'ini paftayla değiştirir; STEP'i değiştirmez. Önceki geometri önizlemesi gerekiyorsa klasörü kopyalayın.

Ölçüler için başlangıç desteği: Excel'de çap işaretli hücreler, son gövdede o çapı taşıyan tek silindir ekseni bulunursa bağlanır. Parçalanmış aynı destek silindirleri tek aday sayılır. Aynı çap birden fazla eksendeyse seçim yapılmaz. Mesafeler yalnız değere göre geometriye bağlanmaz; açık referansı olmayan ölçüler kontrol tablosuna alınır. Sabit JPEG ölçülerinin ve E/F gibi mesafelerin tam otomatik bağlanması bu bağlantının tamamlanmış bir özelliği değildir. Bu nedenle çıktılar üretim onayı verilmiş çizimler olarak sunulmaz.

Testler: `test_cad_script_sheet.py`, `test_cad_recipe_executor.py`, `test_measurement_contract.py`. CadQuery betiği bu komutta tekrar yürütülmez; önceden üretilmiş ve parametreleri kayıtlı STEP kullanılır.

## Açık ölçü referansları

Kayıtlı klasörde `measurements.py` dosyası `build_measurements(p)` fonksiyonunu içerebilir. Geometriyi değiştirmez. Yalnız cadquery/math importları ve fonksiyonlar kabul edilir; işlem başına 60 CPU saniye sınırı ve dosya/ağ erişim denetimi vardır. Model kodu genel işletim sistemi sandbox'ı yerine geçmeyen mevcut kontrollü Python yükleyicisiyle değerlendirilir.

```
/workspace/cq-experiment-venv/bin/python tools/evaluate_script_measurements.py output/saved-script
```

Üretilen measurement-references.json pafta komutunda otomatik okunur. Her kayıt: benzersiz id, source (Excel harfi veya sabit etiket), kind, nominal. diameter için center/axis/radius; radius için center/axis/radius/point; distance/thickness için points (iki nokta) ve direction gerekir. Noktalar dünya mm, yönler birimdir. `unresolved` sebebi de kabul edilir. Excel nominali ve toleransı modelden alınmaz; yerel ayrıştırıcı korunur. Kaynak numarası, son katı üzerindeki geometri ve değer kontrol edilir. Referansın taslaktaki okla anlamsal eşleşmesi ayrıca incelenmelidir. Örneğin aynı değerli iki kalınlık yanlışlıkla birbirine bağlanabilir; BRep kontrolü bunu tek başına ayıramaz.

OCR işareti bulunmayan açık referanslar, doğrulamadan sonra genel yerleşime alınır; metin çakışması çözülemezse ölçü kontrol listesinde kalır. Genel yerleşim, taslaktaki metin konumunu birebir koruma garantisi vermez.

## Görsel kanıt ve yerel konum

`visual-markers.json`: label, view (front/section), centerNormalized ve arrowTipsNormalized içerir. Koordinatlar orijinal JPEG üzerinde 0..1 aralığındadır. OCR ile görünüş çelişkisi reddedilir; ondalık virgül/nokta eşleştirilir. OCR'de olmayan düz etiketler görsel kanıtla eklenebilir. Bu kanıt model kaynaklıdır; bağımsız, kesin görüntü tanıma garantisi değildir.

Doğrusal referansın projeksiyonu görsel ölçü yönüyle uyuşmalıdır. Aynı sayısal değeri taşıyan eksenel/radyal ölçüler birbirinin yerine kabul edilmez. Gerçek silindir/torus desteklerinde, görünmeyen meridyen referansı kesitte görülen eşdeğer meridyene taşınır ve gövdede tekrar doğrulanır. Eksenler arası mesafede malzeme içinde olmayan merkezler gerçek silindir eksenleriyle doğrulanır. Referans düzlemlerinin veya eksenlerinin kapsamı gelecekte ayrı genişletilmelidir; rastgele boşluk noktaları kabul edilmez.

Sayfa çapında boş yer taraması kaldırılmıştır. Yazılar taslak etiketinin yakınında en fazla 64 piksel eksenel kaydırılarak denenir; uzun kılavuzlar reddedilir. Çakışma çözülemiyorsa ölçü rapora alınır. Bu sürüm global optimum çizgi-kesişimi çözümü değildir. Taslak4.7 doğrulaması başka parça ailelerinin de otomatik olarak doğrulandığı anlamına gelmez.

## Zorunlu köşeli parantez filtresi

Paftada yalnız özgün OCR tespitinde köşeli parantezli işareti bulunan ölçüler çizilir. Modelin visual-markers listesi yalnız doğrulama bilgisidir; yeni çizilebilir etiket ekleyemez. Modelin verdiği parantezsiz çap, radyus veya sabit boyut geometrinin kurulmasında kullanılabilir; paftaya ve çözülemeyen ölçü tablosuna alınmaz, placement kaydında omitted olur. Örneğin `[R2]` çizilebilirken `R8` çizilmez; kurallar etiket adına bağlı değildir.

## Dış ölçü şeritleri

Template işaretlerinin piksel merkezi yerine görünüş ve taraf tercihi kullanılır. Gerçek görünüş sınırlarının dışında, kısa açıklıklardan toplam ölçülere doğru şeritler ayrılır. Tolerans dahil gerçek yazı boyutu şerit aralığını belirler. Dar açıklıklarda dış oklar ve çizgi uzantısı kullanılır. Her delik ayrı etiketlenir. Liderlerde dış konumlar tercih edilir; çok uzun bağlantı oluşuyorsa yakın, geometrik mürekkebe değmeyen boşluklar kontrollü ikinci seçenektir. Önceden yerleşmiş ölçü çizgileriyle kesişmeler maliyet olarak değerlendirilir. Algoritma küresel optimum garantisi vermez; sayfa sınırında uygun yer bulunamazsa açık hata döndürür. Ölçek/görünüşlerin otomatik yeniden paketlenmesi bu sürümde uygulanmamıştır.
