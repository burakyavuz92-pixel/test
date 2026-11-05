# Rekor STEP montaj yüzeyi kontrolü

GitHub'a kaydedilen 24 gerçek STEP dosyası XDE adlarıyla yeniden okundu; geometri ve etiketler değiştirilmedi. API çağrısı yapılmadı.

Taslak JPEG'deki @montaj oku, dar boynun ardından geniş flanşın gövdeye bakan düz halka omuz yüzeyini gösteriyor. Bu yüzey beklenen koordinat sisteminde Z=-(C+M), dış normal +Z, iç çap E ve dış çap L ile tanımlanır.

24/24 dosyada montaj adı gerçek bir FACE üzerinde bulundu. Yüzeyin düzlem olması, z konumu, halka sınırlarının çapları, alanı ve dış normali bağımsız olarak kontrol edildi. Tamamı beklenen omuz yüzeyiyle eşleşti. Örneğin 733001 için Z=-38,8 mm, iç çap 20,9 mm, dış çap 25 mm; normal +Z.

STEP'teki ad `montaj`; kaynak JPEG'deki @ öneki adın parçası değildir. Etiket bir noktaya veya bütün katıya değil ilgili yüzeye bağlıdır. Ölçü bağlamasında B için raporlanan belirsizlik bu yüzey etiketini etkilemiyor. Makine sonuçları face-checks.json içinde.
