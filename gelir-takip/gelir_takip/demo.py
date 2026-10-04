"""Arayüzü kayıt girmeden görebilmek için örnek veri (framework'ten bağımsız)."""

from __future__ import annotations

from datetime import date

from .hesaplama import onceki_ay
from .models import TUR_GELIR, TUR_GIDER
from .servis import ButceServisi

# (ayın günü, tutar, kategori, açıklama). Günler her ayda geçerli olacak şekilde seçildi.
_BU_AY = {
    TUR_GIDER: (
        (1, "12000", "Kira", "Daire kirası"),
        (3, "1850", "Fatura", "Elektrik ve doğalgaz"),
        (8, "4200", "Market", "Aylık market"),
        (15, "900", "Ulaşım", "Aylık kart"),
        (22, "650", "Eğlence", "Sinema ve yemek"),
    ),
    TUR_GELIR: ((12, "4750", "Freelance", "Web sitesi tasarımı"),),
}
_ONCEKI_AY = {
    TUR_GIDER: (
        (1, "12000", "Kira", "Daire kirası"),
        (3, "1700", "Fatura", "Elektrik ve doğalgaz"),
        (8, "3900", "Market", "Aylık market"),
        (15, "900", "Ulaşım", "Aylık kart"),
    ),
    TUR_GELIR: ((14, "2500", "Freelance", "Logo çalışması"),),
}


def ornek_veri_ekle(servis: ButceServisi, bugun: date) -> None:
    """Maaş geçmişi (iki ay önce 30.000, bu ay zamlı 32.500) ve son iki aya gider / ek gelir ekler."""
    onceki = onceki_ay(bugun.year, bugun.month)
    iki_ay_once = onceki_ay(*onceki)

    servis.maas_ayarla(*iki_ay_once, "30000")
    servis.maas_ayarla(bugun.year, bugun.month, "32500")

    for (yil, ay), kayitlar in ((onceki, _ONCEKI_AY), ((bugun.year, bugun.month), _BU_AY)):
        for tur, satirlar in kayitlar.items():
            for gun, tutar, kategori, aciklama in satirlar:
                servis.kayit_ekle(tur, date(yil, ay, gun), tutar, kategori, aciklama)
