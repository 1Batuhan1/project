from datetime import date
from decimal import Decimal

import pytest

from gelir_takip.db import GelirDeposu
from gelir_takip.models import Gelir


@pytest.fixture
def depo():
    d = GelirDeposu(":memory:")
    yield d
    d.kapat()


def yeni(tarih, tutar="100", kategori="Maaş", aciklama=""):
    return Gelir(tarih=tarih, tutar=tutar, kategori=kategori, aciklama=aciklama)


def test_ekle_ve_getir(depo):
    kayit = depo.ekle(yeni(date(2026, 10, 4), "1234.56", "Freelance", "site işi"))
    assert kayit.id is not None
    okunan = depo.getir(kayit.id)
    assert okunan == kayit
    assert okunan.tutar == Decimal("1234.56")


def test_olmayan_kayit_none(depo):
    assert depo.getir(999) is None


def test_guncelle(depo):
    kayit = depo.ekle(yeni(date(2026, 10, 4)))
    degisen = Gelir(id=kayit.id, tarih=date(2026, 10, 5), tutar="250.75", kategori="Ek Gelir", aciklama="x")
    assert depo.guncelle(degisen) is True
    assert depo.getir(kayit.id) == degisen


def test_guncelle_olmayan_kayit_false(depo):
    assert depo.guncelle(Gelir(id=42, tarih=date(2026, 1, 1), tutar=1, kategori="a")) is False


def test_guncelle_idsiz_hata(depo):
    with pytest.raises(ValueError):
        depo.guncelle(yeni(date(2026, 1, 1)))


def test_sil(depo):
    kayit = depo.ekle(yeni(date(2026, 10, 4)))
    assert depo.sil(kayit.id) is True
    assert depo.getir(kayit.id) is None
    assert depo.sil(kayit.id) is False


def test_ay_listele_sinirlari_dogru(depo):
    depo.ekle(yeni(date(2026, 9, 30)))   # önceki ay
    depo.ekle(yeni(date(2026, 10, 1)))   # ay başı (dahil)
    depo.ekle(yeni(date(2026, 10, 31)))  # ay sonu (dahil)
    depo.ekle(yeni(date(2026, 11, 1)))   # sonraki ay
    liste = depo.ay_listele(2026, 10)
    assert [g.tarih for g in liste] == [date(2026, 10, 31), date(2026, 10, 1)]


def test_ay_listele_aralik_yil_gecisi(depo):
    depo.ekle(yeni(date(2026, 12, 31)))
    depo.ekle(yeni(date(2027, 1, 1)))
    assert [g.tarih for g in depo.ay_listele(2026, 12)] == [date(2026, 12, 31)]


def test_kullanilan_kategoriler_tekrarsiz(depo):
    depo.ekle(yeni(date(2026, 10, 1), kategori="Zeta"))
    depo.ekle(yeni(date(2026, 10, 2), kategori="alfa"))
    depo.ekle(yeni(date(2026, 10, 3), kategori="Zeta"))
    assert depo.kullanilan_kategoriler() == ["alfa", "Zeta"]


def test_dosyaya_kalici_yazar(tmp_path):
    yol = tmp_path / "alt" / "gelir.db"
    d1 = GelirDeposu(yol)
    d1.ekle(yeni(date(2026, 10, 4), "99.99"))
    d1.kapat()
    d2 = GelirDeposu(yol)
    assert [g.tutar for g in d2.tumunu_listele()] == [Decimal("99.99")]
    d2.kapat()
