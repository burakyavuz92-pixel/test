# Geometri yanıtını yeniden kullanarak devam

`continue-cadquery-group <xlsx> <jpeg> <saved-output> <new-output>` mevcut geometri
ve yüzey etiketi betiklerini yeni, boş klasöre alır; geometriyi tekrar yürütür ve
sadece ölçü bağlama için API çağrısı yapar. Otomatik tekrar değildir; açıkça verilen
ayrı bir komuttur. Tam replay iki yanıtı da kullanır ve API çağırmaz.
Devam komutu kayıtlı pipeline-source SHA256 değerleriyle JPEG/Excel'i karşılaştırır;
farklı girdiyi reddeder. Kullanım raporunda GeometryReused=true ve yalnız bu koşunun
API çağrısı/maliyeti görünür; önceki çağrı maliyeti kendi kaydında kalır.
