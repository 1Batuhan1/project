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
    tr_siralama_anahtari,
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
        ("1,234.56", "1234.56"),       # ABD biçimi: son ayraç ondalıktır
        ("1,234,567", "1234567"),      # virgüllü binlik gruplar
        ("1,234,567.89", "1234567.89"),
        ("1.234.567,89", "1234567.89"),
        ("12,5", "12.5"),
        ("1e3", "1E+3"),
    ],
)
def test_para_ayristir(metin, beklenen):
    assert para_ayristir(metin) == Decimal(beklenen)


@pytest.mark.parametrize(
    "metin",
    [
        "", "   ", "abc", "12,3,4x",
        "NaN", "Infinity", "-Infinity",
        "1,234",      # 1,234 = 1 lira 23,4 kuruş demek olurdu; sessizce 1,23 yapma, kullanıcıya sor
        "10,005", "1234.567", "1.234,567", "1e-3",
        "1,2.3,4",
    ],
)
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


@pytest.mark.parametrize("metin", ["04/10/2026", "04-10-2026", "4.10.2026", " 04.10.2026 "])
def test_tarih_ayristir_farkli_ayraclar(metin):
    assert tarih_ayristir(metin) == date(2026, 10, 4)


@pytest.mark.parametrize("metin", ["", "32.01.2026", "abc", "2026/10/04"])
def test_tarih_ayristir_gecersiz(metin):
    with pytest.raises(ValueError):
        tarih_ayristir(metin)


def test_turkce_siralama():
    adlar = ["Zeta", "Çay", "Eğitim", "Ulaşım", "ılık", "Isı", "İz", "Dolap", "Şeker", "Sağlık", "Ağ", "Kira 2", "Kira", "Ayakkabı"]
    assert sorted(adlar, key=tr_siralama_anahtari) == [
        "Ağ", "Ayakkabı", "Çay", "Dolap", "Eğitim", "ılık", "Isı", "İz", "Kira", "Kira 2", "Sağlık", "Şeker", "Ulaşım", "Zeta",
    ]


def test_turkce_siralama_buyuk_kucuk_harf_ayni():
    assert tr_siralama_anahtari("ÇAY") == tr_siralama_anahtari("çay")
    assert tr_siralama_anahtari("IŞIK") == tr_siralama_anahtari("ışık")   # I -> ı
    assert tr_siralama_anahtari("İNCE") == tr_siralama_anahtari("ince")   # İ -> i
    assert tr_siralama_anahtari("ı") < tr_siralama_anahtari("i")
