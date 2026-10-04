from datetime import date
from decimal import Decimal

import pytest

from gelir_takip.formatting import (
    ay_etiketi,
    oran_bicimle,
    para_ayristir,
    para_bicimle,
    tarih_ayristir,
    tarih_bicimle,
    yuzde_bicimle,
)


@pytest.mark.parametrize(
    "tutar, beklenen",
    [
        (Decimal("0"), "0,00 ₺"),
        (Decimal("5"), "5,00 ₺"),
        (Decimal("1234.5"), "1.234,50 ₺"),
        (Decimal("1234567.89"), "1.234.567,89 ₺"),
        (Decimal("-500"), "−500,00 ₺"),
        (Decimal("-1234.5"), "−1.234,50 ₺"),
        (Decimal("-0.001"), "0,00 ₺"),  # yuvarlayınca sıfır: "−0,00" yazılmaz
    ],
)
def test_para_bicimle(tutar, beklenen):
    assert para_bicimle(tutar) == beklenen


@pytest.mark.parametrize(
    "metin, beklenen",
    [
        ("1.234,56", "1234.56"),
        ("1234,56", "1234.56"),
        ("1234.56", "1234.56"),
        ("1.234", "1234"),
        ("12.5", "12.5"),
        ("500", "500"),
        ("₺ 500", "500"),
        ("2.500,00 TL", "2500.00"),
        ("1.234.567", "1234567"),
    ],
)
def test_para_ayristir(metin, beklenen):
    assert para_ayristir(metin) == Decimal(beklenen)


@pytest.mark.parametrize("metin", ["", "   ", "abc", "12,3,4x"])
def test_para_ayristir_gecersiz(metin):
    with pytest.raises(ValueError):
        para_ayristir(metin)


def test_yuzde_bicimle():
    assert yuzde_bicimle(Decimal("12.5")) == "+%12,5"
    assert yuzde_bicimle(Decimal("-3.0")) == "−%3,0"
    assert yuzde_bicimle(Decimal("0")) == "+%0,0"
    assert yuzde_bicimle(None) == "—"


def test_oran_bicimle():
    assert oran_bicimle(Decimal("52.6")) == "%52,6"
    assert oran_bicimle(Decimal("100")) == "%100,0"


def test_ay_etiketi():
    assert ay_etiketi(2026, 10) == "Ekim 2026"
    assert ay_etiketi(2026, 1) == "Ocak 2026"


def test_tarih_gidis_donus():
    assert tarih_bicimle(date(2026, 10, 4)) == "04.10.2026"
    assert tarih_ayristir("04.10.2026") == date(2026, 10, 4)
    assert tarih_ayristir("2026-10-04") == date(2026, 10, 4)


@pytest.mark.parametrize("metin", ["", "32.01.2026", "abc", "2026/10/04"])
def test_tarih_ayristir_gecersiz(metin):
    with pytest.raises(ValueError):
        tarih_ayristir(metin)
