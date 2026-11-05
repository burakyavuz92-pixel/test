# Excel radyus girdileri

Ölçü sütununda `R8`, `R5`, `r5,5` veya `R 5,5 (±0,1)` kullanılabilir. Ayrıştırıcı nominal sayıyı ayrı tutar; `radiusSymbol` bilgisi API'ye ve sunuma aktarılır. CadQuery fonksiyonu `p[label]` içinde yalnız sayıyı alır. Değer sıfırsa mevcut sıfır ölçü gizleme kuralı korunur. `_METIN` özel sunum metni verdiğinde otomatik R öneki bastırılır; toleranslar mevcut kuralla işlenir.

`checks/RadiusInputChecks.csproj` gerçek bospleyt çalışma kitabını argüman olarak alır; mevcut Excel sunum kontrolleri ayrıca korunur.
