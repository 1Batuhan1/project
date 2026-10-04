"""Tkinter ana penceresi: ay seçici + seçili ayın gelir tablosu."""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import font as tkfont
from tkinter import ttk

from ..formatting import AY_ADLARI, ay_etiketi, para_bicimle, tarih_bicimle
from ..hesaplama import onceki_ay, sonraki_ay
from ..servis import GelirServisi

YIL_ARALIGI = (2000, 2100)

# (kolon id, başlık, genişlik, hizalama)
_KOLONLAR = (
    ("tarih", "Tarih", 100, "center"),
    ("kategori", "Kategori", 140, "w"),
    ("aciklama", "Açıklama", 320, "w"),
    ("tutar", "Tutar", 140, "e"),
)


class AnaPencere(ttk.Frame):
    def __init__(self, ana: tk.Misc, servis: GelirServisi) -> None:
        super().__init__(ana, padding=12)
        self.servis = servis
        bugun = date.today()
        self.yil, self.ay = bugun.year, bugun.month

        self._tema_ayarla()
        self._ust_cubuk_olustur()
        self._tablo_olustur()
        self._alt_cubuk_olustur()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.pack(fill="both", expand=True)

        pencere = self.winfo_toplevel()
        pencere.bind("<Control-Left>", lambda _olay: self.onceki_aya_git())
        pencere.bind("<Control-Right>", lambda _olay: self.sonraki_aya_git())

        self._ay_widgetlarini_guncelle()
        self.yenile()

    # ---- Görünüm kurulumu -------------------------------------------------

    def _tema_ayarla(self) -> None:
        stil = ttk.Style(self)
        for ad in ("vista", "aqua", "clam"):
            if ad in stil.theme_names():
                stil.theme_use(ad)
                break
        stil.configure("Treeview", rowheight=26)

    def _ust_cubuk_olustur(self) -> None:
        cubuk = ttk.Frame(self)
        cubuk.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(cubuk, text="◀", width=3, command=self.onceki_aya_git).pack(side="left")

        self.ay_kutusu = ttk.Combobox(cubuk, state="readonly", values=AY_ADLARI, width=10)
        self.ay_kutusu.pack(side="left", padx=6)
        self.ay_kutusu.bind("<<ComboboxSelected>>", self._ay_kutusu_degisti)

        self.yil_var = tk.StringVar()
        self.yil_kutusu = ttk.Spinbox(
            cubuk,
            from_=YIL_ARALIGI[0],
            to=YIL_ARALIGI[1],
            width=6,
            textvariable=self.yil_var,
            command=self._yil_kutusu_degisti,
        )
        self.yil_kutusu.pack(side="left")
        self.yil_kutusu.bind("<Return>", self._yil_kutusu_degisti)
        self.yil_kutusu.bind("<FocusOut>", self._yil_kutusu_degisti)

        ttk.Button(cubuk, text="▶", width=3, command=self.sonraki_aya_git).pack(side="left", padx=6)
        ttk.Button(cubuk, text="Bugün", command=self.bugune_git).pack(side="left", padx=(12, 0))

    def _tablo_olustur(self) -> None:
        cerceve = ttk.Frame(self)
        cerceve.grid(row=1, column=0, sticky="nsew")
        cerceve.columnconfigure(0, weight=1)
        cerceve.rowconfigure(0, weight=1)

        self.tablo = ttk.Treeview(
            cerceve,
            columns=[kolon[0] for kolon in _KOLONLAR],
            show="headings",
            selectmode="browse",
        )
        for kolon_id, baslik, genislik, hizalama in _KOLONLAR:
            self.tablo.heading(kolon_id, text=baslik, anchor=hizalama)
            self.tablo.column(
                kolon_id, width=genislik, anchor=hizalama, stretch=(kolon_id == "aciklama")
            )
        self.tablo.tag_configure("cift", background="#f3f6fa")

        kaydirma = ttk.Scrollbar(cerceve, orient="vertical", command=self.tablo.yview)
        self.tablo.configure(yscrollcommand=kaydirma.set)
        self.tablo.grid(row=0, column=0, sticky="nsew")
        kaydirma.grid(row=0, column=1, sticky="ns")

        # Ay boşsa tablonun üstünde görünen bilgi yazısı
        self.bos_etiket = ttk.Label(
            cerceve, text="Bu ay için gelir kaydı yok.", foreground="#7a7a7a", background="white"
        )

    def _alt_cubuk_olustur(self) -> None:
        cubuk = ttk.Frame(self)
        cubuk.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        kalin = tkfont.nametofont("TkDefaultFont").copy()
        kalin.configure(weight="bold")
        self._kalin_font = kalin  # Tk, font nesnesini referans tutulmazsa siler

        self.kayit_etiketi = ttk.Label(cubuk)
        self.kayit_etiketi.pack(side="left")
        self.toplam_etiketi = ttk.Label(cubuk, font=kalin)
        self.toplam_etiketi.pack(side="right")

    # ---- Ay seçimi --------------------------------------------------------

    def ay_sec(self, yil: int, ay: int) -> None:
        """(yil, ay)'a geçer. Yıl aralık dışındaysa seçim değişmez."""
        if YIL_ARALIGI[0] <= yil <= YIL_ARALIGI[1] and (yil, ay) != (self.yil, self.ay):
            self.yil, self.ay = yil, ay
            self.yenile()
        self._ay_widgetlarini_guncelle()

    def onceki_aya_git(self) -> None:
        self.ay_sec(*onceki_ay(self.yil, self.ay))

    def sonraki_aya_git(self) -> None:
        self.ay_sec(*sonraki_ay(self.yil, self.ay))

    def bugune_git(self) -> None:
        bugun = date.today()
        self.ay_sec(bugun.year, bugun.month)

    def _ay_widgetlarini_guncelle(self) -> None:
        self.ay_kutusu.current(self.ay - 1)
        self.yil_var.set(str(self.yil))

    def _ay_kutusu_degisti(self, _olay: tk.Event | None = None) -> None:
        self.ay_sec(self.yil, self.ay_kutusu.current() + 1)

    def _yil_kutusu_degisti(self, _olay: tk.Event | None = None) -> None:
        try:
            yil = int(self.yil_var.get())
        except ValueError:
            yil = self.yil  # geçersiz yazıldıysa eski yıla dön
        self.ay_sec(yil, self.ay)

    # ---- Veriyi ekrana yansıtma -------------------------------------------

    def yenile(self) -> None:
        """Seçili ayın kayıtlarını veritabanından okuyup tabloyu ve alt çubuğu günceller."""
        rapor = self.servis.aylik_rapor(self.yil, self.ay)

        self.tablo.delete(*self.tablo.get_children())
        for sira, gelir in enumerate(rapor.gelirler):
            self.tablo.insert(
                "",
                "end",
                iid=str(gelir.id),  # Adım 6'da düzenle/sil için kayıt kimliği
                values=(
                    tarih_bicimle(gelir.tarih),
                    gelir.kategori,
                    gelir.aciklama,
                    para_bicimle(gelir.tutar),
                ),
                tags=("cift",) if sira % 2 else (),
            )

        if rapor.gelirler:
            self.bos_etiket.place_forget()
        else:
            self.bos_etiket.place(relx=0.5, rely=0.4, anchor="center")

        self.kayit_etiketi.configure(text=f"{rapor.ozet.adet} kayıt")
        self.toplam_etiketi.configure(
            text=f"{ay_etiketi(self.yil, self.ay)} toplamı:  {para_bicimle(rapor.ozet.toplam)}"
        )


def calistir(servis: GelirServisi) -> None:
    """Pencereyi açar ve kapanana kadar çalıştırır."""
    kok = tk.Tk()
    kok.title("Gelir Takip")
    kok.geometry("820x520")
    kok.minsize(640, 360)
    AnaPencere(kok, servis)
    try:
        kok.mainloop()
    finally:
        servis.kapat()
