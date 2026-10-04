"""Veri modeli: gider / ek gelir kayıtları ve geçerlilik başlangıcı olan aylık maaş."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

TUR_GELIR = "gelir"  # maaş dışındaki gelirler (freelance, kira geliri ...)
TUR_GIDER = "gider"
TUR_ADLARI = {TUR_GELIR: "Ek gelir", TUR_GIDER: "Gider"}

VARSAYILAN_KATEGORILER = {
    TUR_GELIR: ("Freelance", "Kira Geliri", "Yatırım", "Prim / İkramiye", "Diğer"),
    TUR_GIDER: (
        "Kira", "Fatura", "Market", "Ulaşım", "Yeme-İçme",
        "Sağlık", "Eğitim", "Eğlence", "Borç / Taksit", "Diğer",
    ),
}

YIL_ARALIGI = (2000, 2100)

_KURUS = Decimal("0.01")
_EN_BUYUK_TUTAR = Decimal("999999999999.99")


class GecersizKayitHatasi(ValueError):
    """Kayıt kurallara uymuyor; mesaj kullanıcıya gösterilebilir."""


def _tutar_hazirla(deger: object, *, sifir_olabilir: bool = False) -> Decimal:
    try:
        tutar = Decimal(str(deger)).quantize(_KURUS, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        raise GecersizKayitHatasi("Tutar sayı olmalıdır.") from None
    if not tutar.is_finite():
        raise GecersizKayitHatasi("Tutar sayı olmalıdır.")
    if tutar < 0 or (tutar == 0 and not sifir_olabilir):
        raise GecersizKayitHatasi(
            "Tutar negatif olamaz." if sifir_olabilir else "Tutar sıfırdan büyük olmalıdır."
        )
    if tutar > _EN_BUYUK_TUTAR:
        raise GecersizKayitHatasi("Tutar çok büyük.")
    return tutar


def _yil_dogrula(yil: int) -> None:
    if not YIL_ARALIGI[0] <= yil <= YIL_ARALIGI[1]:
        raise GecersizKayitHatasi(f"Yıl {YIL_ARALIGI[0]} ile {YIL_ARALIGI[1]} arasında olmalıdır.")


@dataclass
class Kayit:
    """Tarihli, kategorili tek bir tutar kaydı. Geçersiz değerle oluşturulamaz."""

    tarih: date
    tutar: Decimal
    kategori: str
    aciklama: str = ""
    id: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.tarih, date):
            raise GecersizKayitHatasi("Tarih geçerli değil.")
        _yil_dogrula(self.tarih.year)

        self.tutar = _tutar_hazirla(self.tutar)

        self.kategori = (self.kategori or "").strip()
        if not self.kategori:
            raise GecersizKayitHatasi("Kategori boş olamaz.")

        self.aciklama = (self.aciklama or "").strip()


@dataclass
class Gelir(Kayit):
    """Maaş dışındaki gelir (ek gelir)."""


@dataclass
class Gider(Kayit):
    """Maaştan düşülen harcama."""


KAYIT_SINIFLARI = {TUR_GELIR: Gelir, TUR_GIDER: Gider}


@dataclass
class Maas:
    """(yil, ay) ayından itibaren geçerli aylık maaş; yenisi girilene kadar sonraki aylara taşınır."""

    yil: int
    ay: int
    tutar: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.yil, int) or not isinstance(self.ay, int) or not 1 <= self.ay <= 12:
            raise GecersizKayitHatasi("Maaşın geçerlilik ayı geçerli değil.")
        _yil_dogrula(self.yil)
        self.tutar = _tutar_hazirla(self.tutar, sifir_olabilir=True)


@dataclass(frozen=True)
class VeriSayilari:
    """Veritabanındaki kayıt adetleri (toplu silme öncesi uyarıda ve sonrasında kullanılır)."""

    gelir: int = 0
    gider: int = 0
    maas: int = 0

    @property
    def toplam(self) -> int:
        return self.gelir + self.gider + self.maas
