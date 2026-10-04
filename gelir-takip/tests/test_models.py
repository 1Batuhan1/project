from datetime import date
from decimal import Decimal

import pytest

from gelir_takip.models import GecersizKayitHatasi, Gelir, Gider, Maas

BUGUN = date(2026, 10, 4)


@pytest.mark.parametrize("sinif", [Gelir, Gider])
def test_gecerli_kayit_olusur_ve_alanlar_temizlenir(sinif):
    k = sinif(tarih=BUGUN, tutar="1500.5", kategori="  Market ", aciklama="  ekim  ")
    assert k.tutar == Decimal("1500.50")
    assert k.kategori == "Market"
    assert k.aciklama == "ekim"
    assert k.id is None


def test_float_tutar_kayan_nokta_hatasi_yapmaz():
    assert Gider(tarih=BUGUN, tutar=0.1 + 0.2, kategori="Diğer").tutar == Decimal("0.30")


def test_tutar_iki_basamaga_yuvarlanir():
    assert Gider(tarih=BUGUN, tutar="10.005", kategori="Diğer").tutar == Decimal("10.01")


@pytest.mark.parametrize("tutar", [0, -5, "0.00", "abc", "", None, "NaN", "Infinity", "1e15"])
def test_gecersiz_tutar_reddedilir(tutar):
    with pytest.raises(GecersizKayitHatasi):
        Gider(tarih=BUGUN, tutar=tutar, kategori="Market")


@pytest.mark.parametrize("kategori", ["", "   ", None])
def test_bos_kategori_reddedilir(kategori):
    with pytest.raises(GecersizKayitHatasi):
        Gider(tarih=BUGUN, tutar=100, kategori=kategori)


@pytest.mark.parametrize("tarih", ["2026-10-04", None, date(1999, 12, 31), date(2101, 1, 1)])
def test_gecersiz_tarih_reddedilir(tarih):
    with pytest.raises(GecersizKayitHatasi):
        Gider(tarih=tarih, tutar=100, kategori="Market")


def test_gelir_ve_gider_birbirine_esit_degil():
    assert Gelir(tarih=BUGUN, tutar=1, kategori="a") != Gider(tarih=BUGUN, tutar=1, kategori="a")


def test_maas_gecerli_ve_sifir_olabilir():
    assert Maas(2026, 10, "32500.5").tutar == Decimal("32500.50")
    assert Maas(2026, 10, 0).tutar == Decimal("0.00")  # örn. işsizlik dönemi


@pytest.mark.parametrize("yil, ay, tutar", [(2026, 0, 100), (2026, 13, 100), (1999, 1, 100), (2026, 1, -1), (2026, 1, "x")])
def test_gecersiz_maas_reddedilir(yil, ay, tutar):
    with pytest.raises(GecersizKayitHatasi):
        Maas(yil, ay, tutar)
