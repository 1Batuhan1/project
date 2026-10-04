"""Türkçe biçimlendirme ve kullanıcı girdisini ayrıştırma yardımcıları."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

AY_ADLARI = (
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
)

_BINLIK_NOKTALI = re.compile(r"^\d{1,3}(\.\d{3})+$")


def ay_adi(ay: int) -> str:
    return AY_ADLARI[ay - 1]


def ay_etiketi(yil: int, ay: int) -> str:
    """(2026, 10) -> 'Ekim 2026'"""
    return f"{ay_adi(ay)} {yil}"


def para_bicimle(tutar: Decimal) -> str:
    """Decimal('1234.5') -> '1.234,50 ₺'"""
    metin = f"{Decimal(tutar):,.2f}"
    metin = metin.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{metin} ₺"


def yuzde_bicimle(oran: Decimal | None) -> str:
    """Decimal('12.5') -> '+%12,5'; None -> '—'"""
    if oran is None:
        return "—"
    metin = f"{oran:+.1f}".replace(".", ",")
    return f"{metin[0]}%{metin[1:]}"


def para_ayristir(metin: str) -> Decimal:
    """Kullanıcının yazdığı tutarı Decimal'e çevirir.

    Kabul edilenler: '1.234,56', '1234,56', '1234.56', '1.234', '₺ 500', '500 TL'
    Geçersizse ValueError fırlatır.
    """
    temiz = (metin or "").replace("₺", "").replace("TL", "").replace("tl", "")
    temiz = temiz.replace(" ", "").strip()
    if not temiz:
        raise ValueError("Tutar boş olamaz.")

    if "," in temiz:
        temiz = temiz.replace(".", "").replace(",", ".")
    elif _BINLIK_NOKTALI.match(temiz):
        temiz = temiz.replace(".", "")

    try:
        return Decimal(temiz)
    except InvalidOperation:
        raise ValueError("Tutar sayı olmalıdır.") from None


def tarih_bicimle(tarih: date) -> str:
    return tarih.strftime("%d.%m.%Y")


def tarih_ayristir(metin: str) -> date:
    """'04.10.2026' veya '2026-10-04' -> date. Geçersizse ValueError."""
    metin = (metin or "").strip()
    for bicim in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(metin, bicim).date()
        except ValueError:
            continue
    raise ValueError("Tarih GG.AA.YYYY biçiminde olmalıdır.")
