from datetime import date
from decimal import Decimal

import pytest

from gelir_takip.models import GecersizGelirHatasi, Gelir

BUGUN = date(2026, 10, 4)


def test_gecerli_gelir_olusur_ve_alanlar_temizlenir():
    g = Gelir(tarih=BUGUN, tutar="1500.5", kategori="  Maaş ", aciklama="  ekim  ")
    assert g.tutar == Decimal("1500.50")
    assert g.kategori == "Maaş"
    assert g.aciklama == "ekim"
    assert g.id is None


def test_float_tutar_kayan_nokta_hatasi_yapmaz():
    assert Gelir(tarih=BUGUN, tutar=0.1 + 0.2, kategori="Diğer").tutar == Decimal("0.30")


def test_tutar_iki_basamaga_yuvarlanir():
    assert Gelir(tarih=BUGUN, tutar="10.005", kategori="Diğer").tutar == Decimal("10.01")


@pytest.mark.parametrize("tutar", [0, -5, "0.00", "abc", "", None, "NaN", "Infinity"])
def test_gecersiz_tutar_reddedilir(tutar):
    with pytest.raises(GecersizGelirHatasi):
        Gelir(tarih=BUGUN, tutar=tutar, kategori="Maaş")


@pytest.mark.parametrize("kategori", ["", "   ", None])
def test_bos_kategori_reddedilir(kategori):
    with pytest.raises(GecersizGelirHatasi):
        Gelir(tarih=BUGUN, tutar=100, kategori=kategori)


def test_gecersiz_tarih_reddedilir():
    with pytest.raises(GecersizGelirHatasi):
        Gelir(tarih="2026-10-04", tutar=100, kategori="Maaş")
