"""Servis katmanı: arayüzlerin (Tkinter / PySide6) kullandığı tek giriş noktası."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from .db import Depo, varsayilan_db_yolu
from .hesaplama import AyKarsilastirma, AylikButce, butce_hesapla, degisim, onceki_ay
from .models import KAYIT_SINIFLARI, TUR_GELIR, TUR_GIDER, VARSAYILAN_KATEGORILER, Kayit, Maas


@dataclass(frozen=True)
class Hareket:
    """Tabloda gösterilecek tek satır: bir gider ya da ek gelir kaydı."""

    tur: str  # TUR_GELIR | TUR_GIDER
    kayit: Kayit


@dataclass(frozen=True)
class AylikRapor:
    hareketler: list[Hareket]                # tarihe göre yeniden eskiye
    maas: Maas | None                        # bu ay geçerli maaş kaydı (None: hiç girilmemiş)
    butce: AylikButce
    kalan_karsilastirma: AyKarsilastirma     # "kalan" tutarının önceki aya göre değişimi


class ButceServisi:
    def __init__(self, depo: Depo | None = None, db_yolu: str | Path | None = None) -> None:
        self._depo = depo or Depo(db_yolu or varsayilan_db_yolu())

    def kapat(self) -> None:
        self._depo.kapat()

    # ---- Maaş -------------------------------------------------------------

    def maas_ayarla(self, yil: int, ay: int, tutar: Decimal | str | float) -> Maas:
        """(yil, ay) ayından itibaren geçerli maaşı kaydeder; önceki aylar değişmez."""
        return self._depo.maaslar.ayarla(yil, ay, tutar)

    def gecerli_maas(self, yil: int, ay: int) -> Maas | None:
        return self._depo.maaslar.gecerli(yil, ay)

    def maas_sil(self, yil: int, ay: int) -> bool:
        return self._depo.maaslar.sil(yil, ay)

    def maas_gecmisi(self) -> list[Maas]:
        return self._depo.maaslar.tumu()

    # ---- Gider / ek gelir kayıtları (tur: TUR_GIDER | TUR_GELIR) ------------

    def kayit_ekle(
        self, tur: str, tarih: date, tutar: Decimal | str | float, kategori: str, aciklama: str = ""
    ) -> Kayit:
        """Doğrular ve kaydeder. Geçersizse GecersizKayitHatasi (ValueError) fırlatır."""
        kayit = KAYIT_SINIFLARI[tur](tarih=tarih, tutar=tutar, kategori=kategori, aciklama=aciklama)
        return self._depo.kayitlar(tur).ekle(kayit)

    def kayit_guncelle(
        self, tur: str, kayit_id: int, tarih: date, tutar: Decimal | str | float, kategori: str, aciklama: str = ""
    ) -> bool:
        kayit = KAYIT_SINIFLARI[tur](id=kayit_id, tarih=tarih, tutar=tutar, kategori=kategori, aciklama=aciklama)
        return self._depo.kayitlar(tur).guncelle(kayit)

    def kayit_sil(self, tur: str, kayit_id: int) -> bool:
        return self._depo.kayitlar(tur).sil(kayit_id)

    def kayit_getir(self, tur: str, kayit_id: int) -> Kayit | None:
        return self._depo.kayitlar(tur).getir(kayit_id)

    def tum_kayitlar(self, tur: str) -> list[Kayit]:
        return self._depo.kayitlar(tur).tumunu_listele()

    def kategoriler(self, tur: str) -> list[str]:
        """Varsayılanlar + kullanıcının daha önce yazdığı kategoriler (tekrarsız)."""
        liste = list(VARSAYILAN_KATEGORILER[tur])
        gorulen = {k.casefold() for k in liste}
        for kategori in self._depo.kayitlar(tur).kullanilan_kategoriler():
            if kategori.casefold() not in gorulen:
                liste.append(kategori)
                gorulen.add(kategori.casefold())
        return liste

    # ---- Rapor ---------------------------------------------------------------

    def _ay_butcesi(self, yil: int, ay: int) -> tuple[list[Kayit], list[Kayit], Maas | None, AylikButce]:
        gelirler = self._depo.gelirler.ay_listele(yil, ay)
        giderler = self._depo.giderler.ay_listele(yil, ay)
        maas = self._depo.maaslar.gecerli(yil, ay)
        return gelirler, giderler, maas, butce_hesapla(maas, gelirler, giderler, yil, ay)

    def aylik_rapor(self, yil: int, ay: int) -> AylikRapor:
        gelirler, giderler, maas, butce = self._ay_butcesi(yil, ay)
        onceki_butce = self._ay_butcesi(*onceki_ay(yil, ay))[3]
        hareketler = sorted(
            [Hareket(TUR_GELIR, k) for k in gelirler] + [Hareket(TUR_GIDER, k) for k in giderler],
            key=lambda h: (h.kayit.tarih, h.kayit.id),
            reverse=True,
        )
        return AylikRapor(
            hareketler=hareketler,
            maas=maas,
            butce=butce,
            kalan_karsilastirma=degisim(butce.kalan, onceki_butce.kalan),
        )
