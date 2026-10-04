"""Tkinter ana penceresi: ay seçici, maaş, sekmeler (Kayıtlar / Özet) ve aylık özet çubuğu."""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from ..formatting import AY_ADLARI, ay_etiketi, para_bicimle, tarih_bicimle
from ..hesaplama import onceki_ay, sonraki_ay
from ..models import TUR_ADLARI, TUR_GELIR, TUR_GIDER, YIL_ARALIGI
from ..servis import ButceServisi
from . import tema
from .formlar import KayitFormu, MaasFormu
from .ozet_sekmesi import OzetSekmesi

# (kolon id, başlık, genişlik, hizalama)
_KOLONLAR = (
    ("tarih", "Tarih", 100, "center"),
    ("tur", "Tür", 80, "center"),
    ("kategori", "Kategori", 130, "w"),
    ("aciklama", "Açıklama", 290, "w"),
    ("tutar", "Tutar", 140, "e"),
)


def _tutar_metni(tur: str, tutar) -> str:
    """Gider eksi, ek gelir artı işaretiyle: '−1.200,00 ₺' / '+4.750,00 ₺'. Sıfırda işaret yok."""
    if not tutar:
        return para_bicimle(tutar)
    return ("−" if tur == TUR_GIDER else "+") + para_bicimle(tutar)


class AnaPencere(ttk.Frame):
    def __init__(self, ana: tk.Misc, servis: ButceServisi) -> None:
        super().__init__(ana, padding=12)
        self.servis = servis
        bugun = date.today()
        self.yil, self.ay = bugun.year, bugun.month

        self._tema_ve_fontlar()
        self._ust_cubuk_olustur()
        self._maas_bolumu_olustur()
        self._sekmeleri_olustur()
        self._ozet_cubugu_olustur()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.pack(fill="both", expand=True)

        pencere = self.winfo_toplevel()
        pencere.bind("<Control-Left>", lambda _olay: self.onceki_aya_git())
        pencere.bind("<Control-Right>", lambda _olay: self.sonraki_aya_git())

        self._ay_widgetlarini_guncelle()
        self.yenile()

    # ---- Görünüm kurulumu -------------------------------------------------

    def _tema_ve_fontlar(self) -> None:
        stil = ttk.Style(self)
        for ad in ("vista", "aqua", "clam"):
            if ad in stil.theme_names():
                stil.theme_use(ad)
                break
        stil.configure("Treeview", rowheight=26)

        # Tk, font nesnesini referans tutulmazsa siler; o yüzden özniteliklerde saklıyoruz
        varsayilan = tkfont.nametofont("TkDefaultFont")
        self._kalin_font = varsayilan.copy()
        self._kalin_font.configure(weight="bold")
        self._buyuk_font = varsayilan.copy()
        boyut = varsayilan.cget("size")
        self._buyuk_font.configure(weight="bold", size=boyut + 3 if boyut > 0 else boyut - 3)

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

    def _maas_bolumu_olustur(self) -> None:
        cerceve = ttk.LabelFrame(self, text="Aylık maaş", padding=(10, 6))
        cerceve.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        cerceve.columnconfigure(1, weight=1)

        self.maas_tutar_etiketi = ttk.Label(cerceve, font=self._buyuk_font)
        self.maas_tutar_etiketi.grid(row=0, column=0, sticky="w")
        self.maas_not_etiketi = ttk.Label(cerceve, foreground=tema.SOLUK)
        self.maas_not_etiketi.grid(row=0, column=1, sticky="w", padx=(14, 0))
        self.maas_dugmesi = ttk.Button(cerceve, command=self.maas_duzenle)
        self.maas_dugmesi.grid(row=0, column=2, sticky="e")

    def _sekmeleri_olustur(self) -> None:
        self.sekmeler = ttk.Notebook(self)
        self.sekmeler.grid(row=2, column=0, sticky="nsew")

        kayitlar = ttk.Frame(self.sekmeler, padding=(0, 10, 0, 0))
        kayitlar.columnconfigure(0, weight=1)
        kayitlar.rowconfigure(1, weight=1)
        self.sekmeler.add(kayitlar, text="  Kayıtlar  ")
        self._arac_cubugu_olustur(kayitlar)
        self._tablo_olustur(kayitlar)

        self.ozet_sekmesi = OzetSekmesi(self.sekmeler)
        self.sekmeler.add(self.ozet_sekmesi, text="  Özet  ")

    def _arac_cubugu_olustur(self, ana: tk.Misc) -> None:
        cubuk = ttk.Frame(ana)
        cubuk.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        ttk.Button(cubuk, text="＋ Gider Ekle", command=lambda: self.kayit_ekle(TUR_GIDER)).pack(side="left")
        ttk.Button(cubuk, text="＋ Ek Gelir Ekle", command=lambda: self.kayit_ekle(TUR_GELIR)).pack(
            side="left", padx=(6, 0)
        )
        # Sağdan sola: Tümünü Sil | ayraç | Sil | Düzenle (yanlışlıkla basılmasın diye tehlikeli olan ayrı durur)
        self.tumunu_sil_dugmesi = ttk.Button(cubuk, text="Tümünü Sil…", command=self.tumunu_sil)
        self.tumunu_sil_dugmesi.pack(side="right")
        ttk.Separator(cubuk, orient="vertical").pack(side="right", fill="y", padx=12, pady=2)
        self.sil_dugmesi = ttk.Button(cubuk, text="Sil", command=self.sil)
        self.sil_dugmesi.pack(side="right")
        self.duzenle_dugmesi = ttk.Button(cubuk, text="Düzenle", command=self.duzenle)
        self.duzenle_dugmesi.pack(side="right", padx=(0, 6))

    def _tablo_olustur(self, ana: tk.Misc) -> None:
        cerceve = ttk.Frame(ana)
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
        self.tablo.tag_configure(TUR_GIDER, foreground=tema.KIRMIZI)
        self.tablo.tag_configure(TUR_GELIR, foreground=tema.YESIL)

        kaydirma = ttk.Scrollbar(cerceve, orient="vertical", command=self.tablo.yview)
        self.tablo.configure(yscrollcommand=kaydirma.set)
        self.tablo.grid(row=0, column=0, sticky="nsew")
        kaydirma.grid(row=0, column=1, sticky="ns")

        self.tablo.bind("<<TreeviewSelect>>", self._secim_degisti)
        self.tablo.bind("<Double-1>", lambda _olay: self.duzenle())
        self.tablo.bind("<Delete>", lambda _olay: self.sil())

        # Ay boşsa tablonun üstünde görünen bilgi yazısı
        self.bos_etiket = ttk.Label(
            cerceve, text="Bu ay için gider veya ek gelir kaydı yok.", foreground=tema.SOLUK, background="white"
        )

    def _ozet_cubugu_olustur(self) -> None:
        cerceve = ttk.Frame(self, padding=(0, 10, 0, 0))
        cerceve.grid(row=3, column=0, sticky="ew")
        self.ozet_degerleri: dict[str, ttk.Label] = {}
        for sutun, (anahtar, baslik) in enumerate(
            (("maas", "Maaş"), ("ek_gelir", "Ek gelir"), ("gider", "Giderler"), ("kalan", "Kalan"))
        ):
            cerceve.columnconfigure(sutun, weight=1)
            ttk.Label(cerceve, text=baslik, foreground=tema.SOLUK).grid(row=0, column=sutun)
            etiket = ttk.Label(cerceve, font=self._buyuk_font if anahtar == "kalan" else self._kalin_font)
            etiket.grid(row=1, column=sutun)
            self.ozet_degerleri[anahtar] = etiket
        self.kayit_sayisi_etiketi = ttk.Label(cerceve, foreground=tema.SOLUK)
        self.kayit_sayisi_etiketi.grid(row=2, column=0, columnspan=4, pady=(6, 0))

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

    def yenile(self, secili: str | None = None) -> None:
        """Seçili ayı veritabanından okuyup maaşı, tabloyu, özet sekmesini ve özet çubuğunu günceller.

        `secili`: yenilemeden sonra seçili hale getirilecek satır ("gider:5" gibi).
        """
        rapor = self.servis.aylik_rapor(self.yil, self.ay)
        butce = rapor.butce

        # Maaş bölümü
        if rapor.maas is None:
            self.maas_tutar_etiketi.configure(text="Girilmedi", foreground=tema.SOLUK)
            self.maas_not_etiketi.configure(text="Bu ay için bir maaş tanımlanmamış.")
            self.maas_dugmesi.configure(text="Maaş Gir")
        else:
            self.maas_tutar_etiketi.configure(text=para_bicimle(rapor.maas.tutar), foreground="")
            baslangic = (rapor.maas.yil, rapor.maas.ay)
            self.maas_not_etiketi.configure(
                text="Bu aydan itibaren geçerli"
                if baslangic == (self.yil, self.ay)
                else f"{ay_etiketi(*baslangic)} ayından beri geçerli (sonraki aylara taşınır)"
            )
            self.maas_dugmesi.configure(text="Maaşı Düzenle")

        # Tablo
        self.tablo.delete(*self.tablo.get_children())
        for sira, hareket in enumerate(rapor.hareketler):
            kayit = hareket.kayit
            self.tablo.insert(
                "",
                "end",
                iid=f"{hareket.tur}:{kayit.id}",
                values=(
                    tarih_bicimle(kayit.tarih),
                    TUR_ADLARI[hareket.tur],
                    kayit.kategori,
                    kayit.aciklama,
                    _tutar_metni(hareket.tur, kayit.tutar),
                ),
                tags=(hareket.tur,) + (("cift",) if sira % 2 else ()),
            )
        if rapor.hareketler:
            self.bos_etiket.place_forget()
        else:
            self.bos_etiket.place(relx=0.5, rely=0.4, anchor="center")
        if secili and self.tablo.exists(secili):
            self.tablo.selection_set(secili)
            self.tablo.see(secili)

        # Özet çubuğu (her sekmenin altında) ve Özet sekmesi
        self.ozet_degerleri["maas"].configure(text=para_bicimle(butce.maas))
        self.ozet_degerleri["ek_gelir"].configure(text=_tutar_metni(TUR_GELIR, butce.ek_gelir.toplam))
        self.ozet_degerleri["gider"].configure(text=_tutar_metni(TUR_GIDER, butce.gider.toplam))
        self.ozet_degerleri["kalan"].configure(
            text=para_bicimle(butce.kalan), foreground=tema.KIRMIZI if butce.kalan < 0 else tema.YESIL
        )
        self.kayit_sayisi_etiketi.configure(
            text=f"{ay_etiketi(self.yil, self.ay)}: {len(rapor.hareketler)} kayıt"
        )
        self.ozet_sekmesi.guncelle(rapor)
        self._secim_degisti()

    # ---- İşlemler -----------------------------------------------------------

    def maas_duzenle(self) -> None:
        MaasFormu(self, self.servis, self.yil, self.ay, kaydedildi=self.yenile)

    def kayit_ekle(self, tur: str) -> None:
        KayitFormu(self, self.servis, tur, self.yil, self.ay, kaydedildi=self._kayit_kaydedildi)

    def duzenle(self) -> None:
        secili = self._secili()
        if secili is None:
            return
        tur, kayit_id = secili
        kayit = self.servis.kayit_getir(tur, kayit_id)
        if kayit is None:  # başka yerden silinmiş
            self.yenile()
            return
        KayitFormu(self, self.servis, tur, self.yil, self.ay, kayit=kayit, kaydedildi=self._kayit_kaydedildi)

    def sil(self) -> None:
        secili = self._secili()
        if secili is None:
            return
        tur, kayit_id = secili
        satir = self.tablo.item(f"{tur}:{kayit_id}", "values")
        onay = messagebox.askyesno(
            "Kaydı sil",
            f"{satir[0]}  {satir[2]}  {satir[4]}\n\nBu kaydı silmek istiyor musunuz?",
            parent=self,
        )
        if onay:
            self.servis.kayit_sil(tur, kayit_id)
            self.yenile()

    def tumunu_sil(self) -> None:
        """Tüm aylardaki gider, ek gelir ve maaş geçmişini siler (hesaplamaya baştan başlamak için)."""
        sayilar = self.servis.veri_sayilari()
        if sayilar.toplam == 0:
            messagebox.showinfo("Tümünü sil", "Silinecek bir kayıt yok.", parent=self)
            return
        onay = messagebox.askyesno(
            "Tümünü sil",
            "TÜM AYLARDAKİ veriler silinecek:\n\n"
            f"   •  {sayilar.gider} gider kaydı\n"
            f"   •  {sayilar.gelir} ek gelir kaydı\n"
            f"   •  {sayilar.maas} maaş kaydı (zam geçmişi dahil)\n\n"
            "Bu işlem GERİ ALINAMAZ. Her şey silinip baştan başlanacak.\n\n"
            "Devam etmek istiyor musunuz?",
            icon="warning",
            default="no",
            parent=self,
        )
        if onay:
            self.servis.tum_verileri_sil()
            self.yenile()

    def _kayit_kaydedildi(self, tur: str, kayit_id: int, tarih: date) -> None:
        """Kaydedilen kaydın ayına geç (farklı aysa) ve satırı seçili göster."""
        self.ay_sec(tarih.year, tarih.month)
        self.yenile(secili=f"{tur}:{kayit_id}")

    def _secili(self) -> tuple[str, int] | None:
        secim = self.tablo.selection()
        if not secim:
            return None
        tur, _, kayit_id = secim[0].partition(":")
        return tur, int(kayit_id)

    def _secim_degisti(self, _olay: tk.Event | None = None) -> None:
        durum = "!disabled" if self.tablo.selection() else "disabled"
        self.duzenle_dugmesi.state([durum])
        self.sil_dugmesi.state([durum])


def calistir(servis: ButceServisi) -> None:
    """Pencereyi açar ve kapanana kadar çalıştırır."""
    kok = tk.Tk()
    kok.title("Gelir Takip")
    kok.geometry("920x740")
    kok.minsize(820, 680)
    AnaPencere(kok, servis)
    try:
        kok.mainloop()
    finally:
        servis.kapat()
