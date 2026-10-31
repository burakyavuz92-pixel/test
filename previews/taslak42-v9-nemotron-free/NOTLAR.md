# Taslak4.2 — Nemotron ücretsiz rota denemesi

Kullanıcının yapılandırdığı model nvidia/nemotron-3.5-super-vl:free. Bu, önceki nvidia/nemotron-3.5-super-vl model adının ücretsiz rotasıdır; başka bir model ailesi olarak değerlendirilmedi.

Aynı JPEG, Excel, v9 sözleşmesi ve tam metin girdisi kullanıldı. İstekte high ve aynı completion sınırı gönderildi. Tek çağrı yapıldı. Girdiler/prompt/yazılım değiştirilmedi.

## Sonuç

İstek 300 saniyelik HttpClient zaman sınırında iptal edildi. Tamamlanmış API yanıtı alınamadı; recipe.json veya api-response.json oluşmadı. Yerel CAD aşaması başlamadı; STEP/JPEG üretilmedi. Otomatik yeniden deneme/onarım çağrısı yok.

Token, reasoning ve maliyet verisi geri dönmedi; bilinmeyen değerler sıfır olarak gösterilmedi. Rotanın ücretsiz adlandırılması kullanım telemetrisi alınmış olduğu anlamına gelmez. Gerçek sağlayıcı da belirlenemedi.

Önceki ücretli istekte yanıt provider=Venice olarak dönmüştü. Bu başarısız isteğin aynı veya farklı sağlayıcıya yönlendirildiğini bilmiyoruz. Gecikmenin kuyruk, çıkarım süresi veya başka bir servis sorunundan kaynaklandığı kanıtlanmadı. Zaman aşımı, hatalı geometri yanıtı veya model ailesinin kalite değerlendirmesiyle aynı şey değildir.

Kullanıcı tercihine uygun olarak başka NVIDIA modeli/rotası veya ek deneme kendiliğinden yapılmadı.
