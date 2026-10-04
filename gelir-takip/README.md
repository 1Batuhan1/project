# Gelir Takip

Aylık gelir girişi, hesaplama ve takip uygulaması (Python, masaüstü).

**Strateji:** önce Tkinter ile hızlıca çalışan bir sürüm, sonra aynı çekirdeğin üzerine
PySide6 ile profesyonel görünümlü arayüz. Bunun mümkün olması için arayüz ile iş mantığı
baştan ayrı tutulur; PySide6'ya geçerken yalnızca `ui_*` klasörü yeniden yazılır.

## Yapı

```
gelir_takip/
  models.py       Gelir kaydı + doğrulama
  formatting.py   1.234,56 ₺ / GG.AA.YYYY biçimleme ve ayrıştırma
  db.py           SQLite (tutarlar kuruş cinsinden tamsayı)
  hesaplama.py    aylık toplam, ortalama, kategori dağılımı, ay karşılaştırma
  servis.py       arayüzlerin tek giriş noktası (GelirServisi)
  ui_tk/          (Adım 5-8)  Tkinter arayüzü
  ui_qt/          (Adım 11)   PySide6 arayüzü
tests/            pytest
```

Arayüz yalnızca `GelirServisi` ve `formatting` ile konuşur; SQLite'ı ya da hesaplamayı bilmez.

## Gereksinimler

- Python 3.10+
- Çekirdek için ek paket yok. Testler için: `pip install -r requirements.txt`
- Tkinter Python ile gelir (Linux'ta gerekirse `sudo apt install python3-tk`)

## Testleri çalıştırma

```
cd gelir-takip
python -m pytest
```

## Yol haritası

| # | Adım | Durum |
|---|------|-------|
| 1 | Gereksinim ve veri modeli | ✅ |
| 2 | Proje iskeleti | ✅ |
| 3 | Veri katmanı (SQLite) | ✅ |
| 4 | İş mantığı + testler | ✅ |
| 5 | Tkinter: ana pencere, ay seçici, gelir tablosu | ⏳ |
| 6 | Tkinter: gelir formu (ekle / düzenle / sil) | ⏳ |
| 7 | Tkinter: özet paneli (toplam, ortalama, değişim, kategori dağılımı) | ⏳ |
| 8 | CSV dışa / içe aktarma | ⏳ |
| 9 | Tkinter sürümünü cilalama ve gözden geçirme | ⏳ |
| 10 | PySide6 tasarım kararları (tema, yerleşim, grafikler) | ⏳ |
| 11 | PySide6 arayüzü (`ui_qt/`) | ⏳ |
| 12 | Paketleme (PyInstaller ile .exe) | ⏳ |
