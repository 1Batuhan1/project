"""Tkinter diyalogları: maaş formu ve gider / ek gelir kayıt formu."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from datetime import date
from tkinter import ttk

from ..formatting import ay_etiketi, para_ayristir, tarih_ayristir, tarih_bicimle
from ..models import TUR_ADLARI, Kayit
from ..servis import ButceServisi


def _tutar_metni(tutar) -> str:
    """Düzenleme kutusuna yazılacak biçim: 1234.5 -> '1234,50' (para_ayristir bunu geri okur)."""
    return f"{tutar:.2f}".replace(".", ",")


class _Diyalog(tk.Toplevel):
    """Ortak iskelet: modal pencere, Enter = kaydet, Esc = iptal, altta hata mesajı ve butonlar."""

    def __init__(self, ana: tk.Misc, baslik: str, kaydet_metni: str = "Kaydet") -> None:
        super().__init__(ana)
        self.title(baslik)
        self.resizable(False, False)
        self.transient(ana.winfo_toplevel())

        self.cerceve = ttk.Frame(self, padding=16)
        self.cerceve.pack(fill="both", expand=True)
        self.cerceve.columnconfigure(1, weight=1)

        self.hata_var = tk.StringVar()
        self._kaydet_metni = kaydet_metni
        self.bind("<Return>", lambda _olay: self.kaydet())
        self.bind("<Escape>", lambda _olay: self.destroy())

    def _alt_cubuk_olustur(self, satir: int) -> None:
        ttk.Label(
            self.cerceve, textvariable=self.hata_var, foreground="#b3261e", wraplength=340
        ).grid(row=satir, column=0, columnspan=2, sticky="w", pady=(8, 0))
        dugmeler = ttk.Frame(self.cerceve)
        dugmeler.grid(row=satir + 1, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(dugmeler, text="İptal", command=self.destroy).pack(side="right", padx=(8, 0))
        self.kaydet_dugmesi = ttk.Button(dugmeler, text=self._kaydet_metni, command=self.kaydet)
        self.kaydet_dugmesi.pack(side="right")

    def _goster(self, ilk_alan: tk.Widget) -> None:
        """Pencereyi ana pencerenin üstünde ortalar, modal yapar ve ilk alana odaklanır."""
        self.update_idletasks()
        ana = self.master.winfo_toplevel()
        x = ana.winfo_rootx() + (ana.winfo_width() - self.winfo_width()) // 2
        y = ana.winfo_rooty() + (ana.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        try:
            self.wait_visibility()
            self.grab_set()
        except tk.TclError:
            pass  # bazı ortamlarda pencere henüz görünür değil; modal olmadan da çalışır
        ilk_alan.focus_set()

    def kaydet(self) -> None:  # alt sınıflar doldurur
        raise NotImplementedError


class MaasFormu(_Diyalog):
    """(yil, ay) ayından itibaren geçerli aylık maaşı girer."""

    def __init__(
        self, ana: tk.Misc, servis: ButceServisi, yil: int, ay: int, kaydedildi: Callable[[], None] | None = None
    ) -> None:
        super().__init__(ana, "Aylık maaş")
        self.servis, self.yil, self.ay, self.kaydedildi = servis, yil, ay, kaydedildi
        mevcut = servis.gecerli_maas(yil, ay)

        ttk.Label(
            self.cerceve,
            text=f"{ay_etiketi(yil, ay)} ayından itibaren geçerli aylık maaş",
            font=("TkDefaultFont", 10, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(self.cerceve, text="Maaş (₺)").grid(row=1, column=0, sticky="w", pady=(12, 0))
        self.tutar_var = tk.StringVar(value=_tutar_metni(mevcut.tutar) if mevcut else "")
        self.tutar_kutusu = ttk.Entry(self.cerceve, textvariable=self.tutar_var, width=22, justify="right")
        self.tutar_kutusu.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(12, 0))

        ttk.Label(
            self.cerceve,
            text=(
                "Bu tutar girdiğiniz aydan itibaren geçerli olur ve siz yenisini girene kadar "
                "sonraki aylara aynen taşınır. Önceki aylar değişmez."
            ),
            foreground="#6b6b6b",
            wraplength=340,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))

        self._alt_cubuk_olustur(3)
        self._goster(self.tutar_kutusu)
        self.tutar_kutusu.selection_range(0, "end")

    def kaydet(self) -> None:
        try:
            self.servis.maas_ayarla(self.yil, self.ay, para_ayristir(self.tutar_var.get()))
        except ValueError as hata:
            self.hata_var.set(str(hata))
            return
        self.destroy()
        if self.kaydedildi:
            self.kaydedildi()


class KayitFormu(_Diyalog):
    """Yeni gider / ek gelir ekler ya da var olanı düzenler."""

    def __init__(
        self,
        ana: tk.Misc,
        servis: ButceServisi,
        tur: str,
        yil: int,
        ay: int,
        kayit: Kayit | None = None,
        kaydedildi: Callable[[str, int, date], None] | None = None,
    ) -> None:
        super().__init__(ana, ("Düzenle: " if kayit else "Yeni ") + TUR_ADLARI[tur])
        self.servis, self.tur, self.kayit, self.kaydedildi = servis, tur, kayit, kaydedildi

        bugun = date.today()
        varsayilan_tarih = bugun if (bugun.year, bugun.month) == (yil, ay) else date(yil, ay, 1)
        kategoriler = servis.kategoriler(tur)

        self.tarih_var = tk.StringVar(value=tarih_bicimle(kayit.tarih if kayit else varsayilan_tarih))
        self.tutar_var = tk.StringVar(value=_tutar_metni(kayit.tutar) if kayit else "")
        self.kategori_var = tk.StringVar(value=kayit.kategori if kayit else kategoriler[0])
        self.aciklama_var = tk.StringVar(value=kayit.aciklama if kayit else "")

        ttk.Label(self.cerceve, text="Tarih").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.cerceve, textvariable=self.tarih_var, width=24).grid(
            row=0, column=1, sticky="ew", padx=(12, 0)
        )
        ttk.Label(self.cerceve, text="Tutar (₺)").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.tutar_kutusu = ttk.Entry(self.cerceve, textvariable=self.tutar_var, width=24, justify="right")
        self.tutar_kutusu.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(8, 0))
        ttk.Label(self.cerceve, text="Kategori").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Combobox(self.cerceve, textvariable=self.kategori_var, values=kategoriler, width=22).grid(
            row=2, column=1, sticky="ew", padx=(12, 0), pady=(8, 0)
        )
        ttk.Label(self.cerceve, text="Açıklama").grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(self.cerceve, textvariable=self.aciklama_var, width=24).grid(
            row=3, column=1, sticky="ew", padx=(12, 0), pady=(8, 0)
        )

        self._alt_cubuk_olustur(4)
        self._goster(self.tutar_kutusu)

    def kaydet(self) -> None:
        try:
            tarih = tarih_ayristir(self.tarih_var.get())
            tutar = para_ayristir(self.tutar_var.get())
            kategori, aciklama = self.kategori_var.get(), self.aciklama_var.get()
            if self.kayit is None:
                kayit_id = self.servis.kayit_ekle(self.tur, tarih, tutar, kategori, aciklama).id
            else:
                kayit_id = self.kayit.id
                if not self.servis.kayit_guncelle(self.tur, kayit_id, tarih, tutar, kategori, aciklama):
                    self.hata_var.set("Bu kayıt artık yok (silinmiş olabilir).")
                    return
        except ValueError as hata:  # GecersizKayitHatasi dahil
            self.hata_var.set(str(hata))
            return
        self.destroy()
        if self.kaydedildi:
            self.kaydedildi(self.tur, kayit_id, tarih)
