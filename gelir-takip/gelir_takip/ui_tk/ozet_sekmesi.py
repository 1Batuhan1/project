"""Ayrıntılı aylık özet sekmesi: önceki aya göre değişim, harcama oranı, kategori dağılımı."""

from __future__ import annotations

import tkinter as tk
from decimal import Decimal
from tkinter import font as tkfont
from tkinter import ttk

from ..formatting import ay_etiketi, oran_bicimle, para_bicimle, tarih_bicimle, yuzde_bicimle
from ..hesaplama import AyKarsilastirma, kategori_paylari
from ..servis import AylikRapor
from . import tema
from .grafikler import DagilimGrafigi, OranCubugu


def _degisim_metni(k: AyKarsilastirma) -> str:
    """'▲ +3.650,00 ₺  (+%26,1)'; değişim yoksa 'değişmedi'."""
    if k.fark == 0:
        return "= değişmedi"
    ok, isaret = ("▲", "+") if k.fark > 0 else ("▼", "−")
    metin = f"{ok} {isaret}{para_bicimle(abs(k.fark))}"
    if k.yuzde_degisim is not None:
        metin += f"  ({yuzde_bicimle(k.yuzde_degisim)})"
    return metin


class OzetSekmesi(ttk.Frame):
    def __init__(self, ana: tk.Misc) -> None:
        super().__init__(ana, padding=14)
        self.columnconfigure(0, weight=1, uniform="ozet")
        self.columnconfigure(1, weight=1, uniform="ozet")

        # Tk, font nesnesini referans tutulmazsa siler
        self._baslik_font = tkfont.nametofont("TkDefaultFont").copy()
        self._baslik_font.configure(weight="bold")

        self._sol_sutunu_olustur()
        self._sag_sutunu_olustur()

    def _baslik(self, ana: tk.Misc, metin: str, satir: int, ust_bosluk: int = 0) -> ttk.Label:
        etiket = ttk.Label(ana, text=metin, font=self._baslik_font)
        etiket.grid(row=satir, column=0, columnspan=3, sticky="w", pady=(ust_bosluk, 6))
        return etiket

    def _sol_sutunu_olustur(self) -> None:
        sol = ttk.Frame(self)
        sol.grid(row=0, column=0, sticky="new", padx=(0, 14))
        sol.columnconfigure(2, weight=1)

        self.karsilastirma_basligi = self._baslik(sol, "Önceki aya göre", 0)
        self._karsilastirma: dict[str, tuple[ttk.Label, ttk.Label]] = {}
        for satir, (anahtar, ad) in enumerate((("kalan", "Kalan"), ("gider", "Giderler")), start=1):
            ttk.Label(sol, text=ad, foreground=tema.SOLUK).grid(row=satir, column=0, sticky="w", pady=2)
            deger = ttk.Label(sol, font=self._baslik_font)
            deger.grid(row=satir, column=1, sticky="w", padx=(14, 14), pady=2)
            degisim = ttk.Label(sol)
            degisim.grid(row=satir, column=2, sticky="w", pady=2)
            self._karsilastirma[anahtar] = (deger, degisim)

        self._baslik(sol, "Harcama oranı", 3, ust_bosluk=18)
        self.oran_cubugu = OranCubugu(sol)
        self.oran_cubugu.grid(row=4, column=0, columnspan=3, sticky="ew")
        self.oran_etiketi = ttk.Label(sol, wraplength=360, justify="left")
        self.oran_etiketi.grid(row=5, column=0, columnspan=3, sticky="w", pady=(6, 0))

        self._baslik(sol, "Gider özeti", 6, ust_bosluk=18)
        self.gider_ozeti_etiketi = ttk.Label(sol, wraplength=360, justify="left")
        self.gider_ozeti_etiketi.grid(row=7, column=0, columnspan=3, sticky="w")

    def _sag_sutunu_olustur(self) -> None:
        sag = ttk.Frame(self)
        sag.grid(row=0, column=1, sticky="new", padx=(14, 0))
        sag.columnconfigure(0, weight=1)

        ttk.Label(sag, text="Gider dağılımı", font=self._baslik_font).grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.gider_grafigi = DagilimGrafigi(sag, tema.BAR_GIDER, "Bu ay gider kaydı yok.")
        self.gider_grafigi.grid(row=1, column=0, sticky="ew")

        ttk.Label(sag, text="Ek gelir dağılımı", font=self._baslik_font).grid(
            row=2, column=0, sticky="w", pady=(18, 6)
        )
        self.gelir_grafigi = DagilimGrafigi(sag, tema.BAR_GELIR, "Bu ay ek gelir kaydı yok.")
        self.gelir_grafigi.grid(row=3, column=0, sticky="ew")

    # ---- Veriyi yansıtma ----------------------------------------------------

    def guncelle(self, rapor: AylikRapor) -> None:
        butce, onceki = rapor.butce, rapor.onceki_butce

        self.karsilastirma_basligi.configure(text=f"Önceki aya göre ({ay_etiketi(onceki.yil, onceki.ay)})")
        if rapor.onceki_veri_var:
            self._karsilastirma_yaz("kalan", butce.kalan, rapor.kalan_karsilastirma, artis_iyi=True)
            self._karsilastirma_yaz("gider", butce.gider.toplam, rapor.gider_karsilastirma, artis_iyi=False)
        else:
            for deger, degisim in self._karsilastirma.values():
                deger.configure(text="—")
                degisim.configure(text="", foreground=tema.SOLUK)
            self._karsilastirma["kalan"][1].configure(text="Önceki ay için veri yok.")

        self._oran_yaz(butce.harcama_orani)

        gider = butce.gider
        if gider.adet == 0:
            self.gider_ozeti_etiketi.configure(text="Bu ay gider kaydı yok.")
        else:
            en_yuksek = gider.en_yuksek
            self.gider_ozeti_etiketi.configure(
                text=(
                    f"{gider.adet} gider · ortalama {para_bicimle(gider.ortalama)}\n"
                    f"En yüksek: {en_yuksek.kategori} — {para_bicimle(en_yuksek.tutar)} "
                    f"({tarih_bicimle(en_yuksek.tarih)})"
                )
            )

        self.gider_grafigi.ciz(kategori_paylari(butce.gider, en_fazla=8))
        self.gelir_grafigi.ciz(kategori_paylari(butce.ek_gelir, en_fazla=5))

    def _karsilastirma_yaz(self, anahtar: str, tutar: Decimal, k: AyKarsilastirma, artis_iyi: bool) -> None:
        deger, degisim = self._karsilastirma[anahtar]
        deger.configure(text=para_bicimle(tutar))
        if k.fark == 0:
            renk = tema.SOLUK
        else:
            renk = tema.YESIL if (k.fark > 0) == artis_iyi else tema.KIRMIZI
        degisim.configure(text=_degisim_metni(k), foreground=renk)

    def _oran_yaz(self, oran: Decimal | None) -> None:
        self.oran_cubugu.ayarla(oran)
        if oran is None:
            self.oran_etiketi.configure(text="Bu ay için maaş ya da ek gelir girilmemiş.", foreground=tema.SOLUK)
        elif oran > 100:
            self.oran_etiketi.configure(
                text=f"{oran_bicimle(oran)}: giderler geliri aştı.", foreground=tema.KIRMIZI
            )
        else:
            self.oran_etiketi.configure(
                text=f"{oran_bicimle(oran)}  (giderler ÷ maaş + ek gelir)", foreground=""
            )
