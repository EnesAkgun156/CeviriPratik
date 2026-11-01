# Pratik Çeviri

Klasör yapısı:
- `index.html` -> GitHub Pages'e yüklenen site (tek dosya)
- `api/main.py`, `api/requirements.txt` -> Python (FastAPI + Gemini) sunucusu

## 1) API'yi çalıştır
Yerelde test:
    cd api
    pip install -r requirements.txt
    export GEMINI_API_KEY="anahtarin"        # Windows: set GEMINI_API_KEY=anahtarin
    uvicorn main:app --reload --port 8000

GitHub Pages https olduğu için canlıda API adresin de https olmalı (Render, Railway, Fly.io vb.).
Render örneği: Root Directory `api`, Build `pip install -r requirements.txt`,
Start `uvicorn main:app --host 0.0.0.0 --port $PORT`.
Ortam değişkenleri: GEMINI_API_KEY ve ALLOWED_ORIGINS=https://KULLANICIADI.github.io

## 2) Siteyi bağla
- `index.html` içinde `const DEFAULT_API=""` satırına API adresini yaz (sonunda / olmadan), veya
- siteyi aç -> profil ekranının altındaki "API ayarları" kutusuna adresi yaz, Kaydet.

## 3) GitHub Pages
1. Yeni repo aç, `index.html` dosyasını ana dizine yükle (api klasörünü de yükleyebilirsin; anahtar içermez).
2. Settings -> Pages -> Deploy from a branch -> main / (root) -> Save.
3. Adres: https://KULLANICIADI.github.io/REPO-ADI/

Notlar: Puanlar, profiller ve şifreler ziyaretçinin tarayıcısında saklanır (cihaza özeldir).
Enes ve Seda'nın varsayılan şifreleri sayfa kodunda görünür; gerçek güvenlik sağlamaz.
