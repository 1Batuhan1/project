"""Veri modeli: tek bir gelir kaydı ve doğrulama kuralları."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

VARSAYILAN_KATEGORILER = (
    "Maaş",
    "Ek Gelir",
    "Freelance",
    "Kira Geliri",
    "Yatırım",
    "Diğer",
)

_KURUS = Decimal("0.01")


class GecersizGelirHatasi(ValueError):
    """Gelir kaydı kurallara uymuyor; mesaj kullanıcıya gösterilebilir."""


@dataclass
class Gelir:
    """Tek bir gelir kaydı. Geçersiz değerle oluşturulamaz."""

    tarih: date
    tutar: Decimal
    kategori: str
    aciklama: str = ""
    id: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.tarih, date):
            raise GecersizGelirHatasi("Tarih geçerli değil.")

        try:
            tutar = Decimal(str(self.tutar)).quantize(_KURUS, rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError):
            raise GecersizGelirHatasi("Tutar sayı olmalıdır.") from None
        if not tutar.is_finite() or tutar <= 0:
            raise GecersizGelirHatasi("Tutar sıfırdan büyük olmalıdır.")
        self.tutar = tutar

        self.kategori = (self.kategori or "").strip()
        if not self.kategori:
            raise GecersizGelirHatasi("Kategori boş olamaz.")

        self.aciklama = (self.aciklama or "").strip()
