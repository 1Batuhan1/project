from datetime import date
from decimal import Decimal

from gelir_takip.db import GelirDeposu
from gelir_takip.hesaplama import aylik_ozet, karsilastir, onceki_ay, sonraki_ay
from gelir_takip.models import Gelir
from gelir_takip.servis import GelirServisi


def g(tarih, tutar, kategori="Maaş"):
    return Gelir(tarih=tarih, tutar=tutar, kategori=kategori)


def test_bos_ay_ozeti_sifir():
    ozet = aylik_ozet([], 2026, 10)
    assert ozet.toplam == Decimal("0.00")
    assert ozet.adet == 0
    assert ozet.ortalama == Decimal("0.00")
    assert ozet.en_yuksek is None
    assert ozet.kategori_toplamlari == {}


def test_toplam_ortalama_en_yuksek():
    liste = [
        g(date(2026, 10, 1), "1000", "Maaş"),
        g(date(2026, 10, 15), "500.50", "Freelance"),
        g(date(2026, 10, 20), "250", "Freelance"),
    ]
    ozet = aylik_ozet(liste, 2026, 10)
    assert ozet.toplam == Decimal("1750.50")
    assert ozet.adet == 3
    assert ozet.ortalama == Decimal("583.50")
    assert ozet.en_yuksek.tutar == Decimal("1000.00")


def test_baska_aylarin_kayitlari_sayilmaz():
    liste = [g(date(2026, 9, 30), "999"), g(date(2026, 10, 1), "100"), g(date(2025, 10, 1), "999")]
    assert aylik_ozet(liste, 2026, 10).toplam == Decimal("100.00")


def test_kategori_toplamlari_buyukten_kucuge():
    liste = [
        g(date(2026, 10, 1), "100", "B"),
        g(date(2026, 10, 2), "300", "A"),
        g(date(2026, 10, 3), "200", "B"),
    ]
    ozet = aylik_ozet(liste, 2026, 10)
    assert list(ozet.kategori_toplamlari.items()) == [("A", Decimal("300.00")), ("B", Decimal("300.00"))]


def test_kategori_esitlikte_isme_gore_sirali():
    liste = [g(date(2026, 10, 1), "100", "Z"), g(date(2026, 10, 2), "100", "A")]
    assert list(aylik_ozet(liste, 2026, 10).kategori_toplamlari) == ["A", "Z"]


def test_ortalama_yuvarlama():
    liste = [g(date(2026, 10, 1), "10"), g(date(2026, 10, 2), "10"), g(date(2026, 10, 3), "10.01")]
    assert aylik_ozet(liste, 2026, 10).ortalama == Decimal("10.00")


def test_ay_gecisleri():
    assert onceki_ay(2026, 1) == (2025, 12)
    assert onceki_ay(2026, 10) == (2026, 9)
    assert sonraki_ay(2026, 12) == (2027, 1)
    assert sonraki_ay(2026, 10) == (2026, 11)


def test_karsilastir_artis_ve_dusus():
    onceki = aylik_ozet([g(date(2026, 9, 1), "1000")], 2026, 9)
    artis = karsilastir(aylik_ozet([g(date(2026, 10, 1), "1250")], 2026, 10), onceki)
    assert artis.fark == Decimal("250.00")
    assert artis.yuzde_degisim == Decimal("25.0")
    dusus = karsilastir(aylik_ozet([g(date(2026, 10, 1), "900")], 2026, 10), onceki)
    assert dusus.fark == Decimal("-100.00")
    assert dusus.yuzde_degisim == Decimal("-10.0")


def test_karsilastir_onceki_ay_bossa_yuzde_yok():
    bos = aylik_ozet([], 2026, 9)
    sonuc = karsilastir(aylik_ozet([g(date(2026, 10, 1), "500")], 2026, 10), bos)
    assert sonuc.fark == Decimal("500.00")
    assert sonuc.yuzde_degisim is None


def test_servis_aylik_rapor_uctan_uca():
    servis = GelirServisi(depo=GelirDeposu(":memory:"))
    servis.gelir_ekle(date(2026, 9, 10), "2000", "Maaş")
    servis.gelir_ekle(date(2026, 10, 5), "2500", "Maaş", "zamlı")
    servis.gelir_ekle(date(2026, 10, 12), "500", "Freelance")
    rapor = servis.aylik_rapor(2026, 10)
    assert len(rapor.gelirler) == 2
    assert rapor.ozet.toplam == Decimal("3000.00")
    assert rapor.karsilastirma.onceki_toplam == Decimal("2000.00")
    assert rapor.karsilastirma.yuzde_degisim == Decimal("50.0")
    servis.kapat()


def test_servis_ocak_icin_onceki_yil_aralik():
    servis = GelirServisi(depo=GelirDeposu(":memory:"))
    servis.gelir_ekle(date(2025, 12, 31), "100", "Maaş")
    servis.gelir_ekle(date(2026, 1, 1), "150", "Maaş")
    assert servis.aylik_rapor(2026, 1).karsilastirma.onceki_toplam == Decimal("100.00")
    servis.kapat()


def test_servis_kategoriler_varsayilan_ve_ozel_tekrarsiz():
    servis = GelirServisi(depo=GelirDeposu(":memory:"))
    servis.gelir_ekle(date(2026, 10, 1), "10", "Burs")
    servis.gelir_ekle(date(2026, 10, 2), "10", "maaş")  # varsayılanın küçük harfli hali
    kategoriler = servis.kategoriler()
    assert "Burs" in kategoriler
    assert [k.casefold() for k in kategoriler].count("maaş") == 1
    servis.kapat()
