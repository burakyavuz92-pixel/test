# Çalışma raporu

Durum: failed-with-report

- **API_AUTHENTICATION / configuration / error**: OpenRouter HTTP 401 Unauthorized. Model analizi alınamadı; Excel/JPEG yorumlaması değerlendirilemedi.
- Aksiyon: bulut ortamındaki OPENROUTER_API_KEY ve sağlayıcı erişimini kontrol edin; anahtarı sohbete yazmayın.

Dört satır ayrıştırıldı ve istek hazırlandı. Bir HTTP isteği, sıfır tamamlanmış model yanıtı, sıfır JPEG. Sağlayıcı usage/maliyet bilgisi alınamadı; JSON içindeki 0 doğrulanmış fatura bilgisi değildir. İlk hatanın sınıfı, yeni kod politikasına göre yerelde düzeltildi; ikinci API isteği yapılmadı.
