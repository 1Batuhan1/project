"""Arayüzü kayıt girmeden görebilmek için örnek veri (framework'ten bağımsız)."""

from __future__ import annotations

from datetime import date

from .hesaplama import onceki_ay
from .servis import GelirServisi

# (ayın günü, tutar, kategori, açıklama). Günler her ayda geçerli olacak şekilde seçildi.
_BU_AY = (
    (1, "32500", "Maaş", "Aylık maaş"),
    (5, "8000", "Kira Geliri", "Daire kirası"),
    (12, "4750", "Freelance", "Web sitesi tasarımı"),
    (18, "1234.56", "Yatırım", "Temettü"),
    (25, "850", "Ek Gelir", "İkinci el satış"),
)
_ONCEKI_AY = (
    (1, "30000", "Maaş", "Aylık maaş"),
    (5, "8000", "Kira Geliri", "Daire kirası"),
    (14, "2500", "Freelance", "Logo çalışması"),
)


def ornek_veri_ekle(servis: GelirServisi, bugun: date) -> None:
    """Bugünün ayına ve bir önceki aya örnek gelirler ekler."""
    onceki_yil, onceki_ay_no = onceki_ay(bugun.year, bugun.month)
    for yil, ay, kayitlar in (
        (onceki_yil, onceki_ay_no, _ONCEKI_AY),
        (bugun.year, bugun.month, _BU_AY),
    ):
        for gun, tutar, kategori, aciklama in kayitlar:
            servis.gelir_ekle(date(yil, ay, gun), tutar, kategori, aciklama)
