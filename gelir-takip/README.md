# Gelir Takip

Aylık maaş, gider ve ek gelir takibi: **Kalan = Maaş + Ek gelir − Giderler** (Python, masaüstü).

**Maaş kuralı:** Maaş bir kez girilir ve yenisi girilene kadar sonraki aylara taşınır. Zam olunca
"bu aydan itibaren" yeni tutar girilir; önceki aylar eski maaşıyla kalır, geçmiş hesaplar bozulmaz.

**Strateji:** önce Tkinter ile hızlıca çalışan bir sürüm, sonra aynı çekirdeğin üzerine
PySide6 ile profesyonel görünümlü arayüz. Bunun mümkün olması için arayüz ile iş mantığı
baştan ayrı tutulur; PySide6'ya geçerken yalnızca `ui_*` klasörü yeniden yazılır.

## Yapı

```
gelir_takip/
  models.py       Gider / Gelir (ek gelir) kaydı, Maas (geçerlilik başlangıcı ile) + doğrulama
  formatting.py   1.234,56 ₺ / GG.AA.YYYY biçimleme ve ayrıştırma
  db.py           SQLite: gelir, gider, maas tabloları (tutarlar kuruş cinsinden tamsayı)
  hesaplama.py    aylık özet, bütçe (kalan, harcama oranı), ay karşılaştırma
  servis.py       arayüzlerin tek giriş noktası (ButceServisi)
  demo.py         --demo için örnek veri
  ui_tk/          Tkinter arayüzü (ana_pencere, formlar, ozet_sekmesi, grafikler, tema)
  ui_qt/          (Adım 11)   PySide6 arayüzü
tests/            pytest
```

Arayüz yalnızca `ButceServisi` ve `formatting` ile konuşur; SQLite'ı ya da hesaplamayı bilmez.

## Gereksinimler

- Python 3.10+
- Çekirdek için ek paket yok. Testler için: `pip install -r requirements.txt`
- Tkinter Python ile gelir (Linux'ta gerekirse `sudo apt install python3-tk`)

## Uygulamayı çalıştırma

```
python -m gelir_takip --demo     # örnek verilerle aç (kayıt tutmaz, deneme için)
python -m gelir_takip            # gerçek kullanım: ~/.gelir_takip/gelir.db
python -m gelir_takip --db yol/gelir.db   # başka bir veritabanı dosyası
```

Kullanım: **Maaşı Düzenle** ile maaş girilir; **＋ Gider Ekle / ＋ Ek Gelir Ekle** ile kayıt eklenir.
Satıra çift tıkla = düzenle, `Delete` = sil, `Ctrl+←` / `Ctrl+→` = önceki / sonraki ay.

- **Özet sekmesi:** önceki aya göre kalan ve gider değişimi, harcama oranı çubuğu, gider özeti
  (adet, ortalama, en yüksek) ve kategori dağılımları.
- **Tümünü Sil…:** hesaplamaya baştan başlamak için TÜM aylardaki gider, ek gelir ve maaş geçmişini siler.
  Silmeden önce kaç kaydın gideceği gösterilir ve onay istenir (varsayılan buton "Hayır"). Geri alınamaz.

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
| 5 | Tkinter: ana pencere, ay seçici, gelir tablosu | ✅ |
| 6 | Tkinter: maaş formu + gider / ek gelir formu (ekle / düzenle / sil) | ✅ |
| 7 | Tkinter: ayrıntılı özet (önceki ayla karşılaştırma, harcama oranı, kategori dağılımı) + Tümünü Sil | ✅ |
| 8 | CSV dışa / içe aktarma | ⏳ |
| 9 | Tkinter sürümünü cilalama ve gözden geçirme | ⏳ |
| 10 | PySide6 tasarım kararları (tema, yerleşim, grafikler) | ⏳ |
| 11 | PySide6 arayüzü (`ui_qt/`) | ⏳ |
| 12 | Paketleme (PyInstaller ile .exe) | ⏳ |
