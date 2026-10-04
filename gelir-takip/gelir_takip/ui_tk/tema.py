"""Tkinter arayüzünün renkleri (PySide6 sürümü ui_qt/ içinde kendi temasını tanımlar)."""

from __future__ import annotations

from decimal import Decimal

YESIL = "#1b7f3b"
KIRMIZI = "#b3261e"
SOLUK = "#6b6b6b"

KART_ZEMIN = "white"
KART_CERCEVE = "#c8ccd0"
IZ_RENGI = "#e9edf2"      # çubuk grafiklerinin boş kısmı
BAR_GIDER = "#e0847c"
BAR_GELIR = "#6cbf86"


def oran_rengi(oran: Decimal) -> str:
    """Harcama oranı çubuğunun rengi: rahat (yeşil), sınırda (turuncu), gelir aşıldı (kırmızı)."""
    if oran <= 75:
        return "#4caf72"
    if oran <= 100:
        return "#e0a030"
    return "#c0392b"
