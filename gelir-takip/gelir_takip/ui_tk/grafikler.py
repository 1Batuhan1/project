"""Basit Canvas grafikleri: harcama oranı çubuğu ve kategori dağılımı."""

from __future__ import annotations

import tkinter as tk
from decimal import Decimal
from tkinter import font as tkfont

from ..formatting import oran_bicimle, para_bicimle
from ..hesaplama import KategoriPayi
from . import tema


class OranCubugu(tk.Canvas):
    """0-%100 arası dolan yatay çubuk. %100'ü aşan oran çubuğu tamamen doldurur ve kırmızıya döner."""

    YUKSEKLIK = 16

    def __init__(self, ana: tk.Misc) -> None:
        super().__init__(ana, height=self.YUKSEKLIK, highlightthickness=0, background=tema.KART_ZEMIN)
        self._oran: Decimal | None = None
        self.bind("<Configure>", lambda _olay: self._ciz())

    def ayarla(self, oran: Decimal | None) -> None:
        self._oran = oran
        self._ciz()

    def _ciz(self) -> None:
        self.delete("all")
        genislik = max(self.winfo_width(), 4)
        self.create_rectangle(0, 0, genislik - 1, self.YUKSEKLIK - 1, fill=tema.IZ_RENGI, outline=tema.KART_CERCEVE)
        if self._oran is not None and self._oran > 0:
            dolu = max(1.0, (genislik - 3) * min(float(self._oran), 100.0) / 100)
            self.create_rectangle(1, 1, 1 + dolu, self.YUKSEKLIK - 2, fill=tema.oran_rengi(self._oran), outline="")


class DagilimGrafigi(tk.Canvas):
    """Kategori başına yatay çubuk: ad | çubuk | tutar | yüzde. Genişliğe göre kendini yeniden çizer."""

    SATIR = 26
    ADLAR_GENISLIGI = 140  # "Diğer kategoriler" sığacak kadar
    KENAR = 10

    def __init__(self, ana: tk.Misc, bar_rengi: str, bos_metin: str) -> None:
        super().__init__(
            ana,
            height=self.SATIR + 8,
            highlightthickness=1,
            highlightbackground=tema.KART_CERCEVE,
            background=tema.KART_ZEMIN,
        )
        self._font = tkfont.nametofont("TkDefaultFont")
        self._bar_rengi = bar_rengi
        self._bos_metin = bos_metin
        self._paylar: list[KategoriPayi] = []
        self.bind("<Configure>", lambda _olay: self._ciz())

    def ciz(self, paylar: list[KategoriPayi]) -> None:
        self._paylar = list(paylar)
        self.configure(height=max(len(self._paylar), 1) * self.SATIR + 8)
        self._ciz()

    def _kisalt(self, metin: str) -> str:
        if self._font.measure(metin) <= self.ADLAR_GENISLIGI:
            return metin
        while metin and self._font.measure(metin + "…") > self.ADLAR_GENISLIGI:
            metin = metin[:-1]
        return metin + "…"

    def _ciz(self) -> None:
        self.delete("all")
        genislik = self.winfo_width()
        if not self._paylar:
            self.create_text(
                self.KENAR, (self.SATIR + 8) / 2, text=self._bos_metin, anchor="w", fill=tema.SOLUK, font=self._font
            )
            return

        tutarlar = [para_bicimle(p.tutar) for p in self._paylar]
        yuzdeler = [oran_bicimle(p.yuzde) for p in self._paylar]
        yuzde_genisligi = max(self._font.measure(m) for m in yuzdeler)
        tutar_genisligi = max(self._font.measure(m) for m in tutarlar)

        yuzde_sag = genislik - self.KENAR
        tutar_sag = yuzde_sag - yuzde_genisligi - 14
        bar_x0 = self.KENAR + self.ADLAR_GENISLIGI + 8
        bar_genisligi = max(tutar_sag - tutar_genisligi - 12 - bar_x0, 20)

        for sira, pay in enumerate(self._paylar):
            y = 4 + sira * self.SATIR + self.SATIR / 2
            self.create_text(self.KENAR, y, text=self._kisalt(pay.kategori), anchor="w", font=self._font)
            self.create_rectangle(bar_x0, y - 5, bar_x0 + bar_genisligi, y + 5, fill=tema.IZ_RENGI, outline="")
            dolu = bar_genisligi * float(pay.yuzde) / 100
            if dolu > 0:
                self.create_rectangle(bar_x0, y - 5, bar_x0 + max(dolu, 2), y + 5, fill=self._bar_rengi, outline="")
            self.create_text(tutar_sag, y, text=tutarlar[sira], anchor="e", font=self._font)
            self.create_text(yuzde_sag, y, text=yuzdeler[sira], anchor="e", fill=tema.SOLUK, font=self._font)
