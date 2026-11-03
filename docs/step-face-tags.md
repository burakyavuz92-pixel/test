# STEP montaj yüzü adları

`@isim` işareti STEP-only yüz etiketi; köşeli parantezli ölçülerden ayrıdır. Model ölçü aşamasında face_tags_script alanıyla build_face_tags(p) döndürür. Bu fonksiyon name, surface, point döndürür. Desteklenen yüzler düzlem ve silindirdir; analitik destek ile gerçek kırpılmış yüzde bulunan nokta birlikte tek yüz seçmelidir. Yüz yoksa, belirsizse veya isim yineleniyorsa işlem başarısızdır. İsimler parça içinde benzersizdir. Geometri üretim kodu değiştirilmez.

Pipeline ölçü aşamasından sonra yüzleri STEP'e yazar; pafta katmanı bu etiketleri kullanmaz. Replay klasöründe isteğe bağlı face-tags.py saklanır. Yerel yardımcı: `python tools/tag_script_steps.py output/folder` (CadQuery ortamı).

## Montaj yazılımında okuma

OCCT STEPCAFControl_Reader ve XCAF belge yapısı kullanılır. SetNameMode(True) yanında Interface_Static.SetIVal_s('read.stepcaf.subshapes.name',1) gerekir. Yazarken karşılığı write.stepcaf.subshapes.name=1'dir. Normal STEPControl_Reader geometriyi okur; yüz adları için tek başına yeterli değildir. XCAF ShapeTool.GetFreeShapes → GetSubShapes üzerinde TDataStd_Name okunur. Adla bulunan nesnenin TopAbs_FACE olduğu kontrol edilir. tools/step_face_tags.py read_tags fonksiyonu çalışan örnektir.

STEP yazımı geçici dosyaya yapılır; isimler ve yüz alan/merkezleri geri okunup karşılaştırılır, katı hacmi/geçerliliği doğrulanır, sonra asıl dosya atomik değiştirilir. SolidWorks'te yüz adının arayüzde gösterilmesi doğrulanmamıştır; hedef OCCT montaj yazılımıdır. Yeniden geometrik modellemede adlar otomatik kararlı yüz kimliği değildir; her yeni üretimde seçici tekrar doğrulanır.

Test: düzlem ve silindir adlarının dönüşü, farklı kalınlıklar, olmayan yüz, delik boşluğuna denk gelen nokta ve tekrar isim reddi. Yerel altı gerçek geometride montaj etiketi roundtrip doğrulandı. API modelinin 4.8 oku yorumlaması onay engeli nedeniyle henüz doğrulanmadı.
