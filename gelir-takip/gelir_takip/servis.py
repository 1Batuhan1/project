"""Servis katmanı: arayüzlerin (Tkinter / PySide6) kullandığı tek giriş noktası."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from .db import GelirDeposu, varsayilan_db_yolu
from .hesaplama import AyKarsilastirma, AylikOzet, aylik_ozet, karsilastir, onceki_ay
from .models import VARSAYILAN_KATEGORILER, Gelir


@dataclass(frozen=True)
class AylikRapor:
    gelirler: list[Gelir]
    ozet: AylikOzet
    karsilastirma: AyKarsilastirma


class GelirServisi:
    def __init__(self, depo: GelirDeposu | None = None, db_yolu: str | Path | None = None) -> None:
        self._depo = depo or GelirDeposu(db_yolu or varsayilan_db_yolu())

    def kapat(self) -> None:
        self._depo.kapat()

    def gelir_ekle(self, tarih: date, tutar: Decimal | str | float, kategori: str, aciklama: str = "") -> Gelir:
        """Doğrular ve kaydeder. Geçersizse GecersizGelirHatasi fırlatır."""
        return self._depo.ekle(Gelir(tarih=tarih, tutar=tutar, kategori=kategori, aciklama=aciklama))

    def gelir_guncelle(
        self, gelir_id: int, tarih: date, tutar: Decimal | str | float, kategori: str, aciklama: str = ""
    ) -> bool:
        return self._depo.guncelle(
            Gelir(id=gelir_id, tarih=tarih, tutar=tutar, kategori=kategori, aciklama=aciklama)
        )

    def gelir_sil(self, gelir_id: int) -> bool:
        return self._depo.sil(gelir_id)

    def gelir_getir(self, gelir_id: int) -> Gelir | None:
        return self._depo.getir(gelir_id)

    def tum_gelirler(self) -> list[Gelir]:
        return self._depo.tumunu_listele()

    def kategoriler(self) -> list[str]:
        """Varsayılanlar + kullanıcının daha önce yazdığı kategoriler (tekrarsız)."""
        liste = list(VARSAYILAN_KATEGORILER)
        gorulen = {k.casefold() for k in liste}
        for kategori in self._depo.kullanilan_kategoriler():
            if kategori.casefold() not in gorulen:
                liste.append(kategori)
                gorulen.add(kategori.casefold())
        return liste

    def aylik_rapor(self, yil: int, ay: int) -> AylikRapor:
        gelirler = self._depo.ay_listele(yil, ay)
        onceki_yil, onceki_ay_no = onceki_ay(yil, ay)
        bu_ay = aylik_ozet(gelirler, yil, ay)
        onceki = aylik_ozet(self._depo.ay_listele(onceki_yil, onceki_ay_no), onceki_yil, onceki_ay_no)
        return AylikRapor(gelirler=gelirler, ozet=bu_ay, karsilastirma=karsilastir(bu_ay, onceki))
