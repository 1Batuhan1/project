from datetime import date
from decimal import Decimal

from gelir_takip.db import Depo
from gelir_takip.hesaplama import (
    DIGER_KATEGORILER,
    aylik_ozet,
    butce_hesapla,
    degisim,
    karsilastir,
    kategori_paylari,
    onceki_ay,
    sonraki_ay,
)
from gelir_takip.models import Gelir, Gider, Maas
from gelir_takip.servis import ButceServisi


def g(tarih, tutar, kategori="Freelance"):
    return Gelir(tarih=tarih, tutar=tutar, kategori=kategori)


def gider(tarih, tutar, kategori="Market"):
    return Gider(tarih=tarih, tutar=tutar, kategori=kategori)


# ---- Aylık özet --------------------------------------------------------------

def test_bos_ay_ozeti_sifir():
    ozet = aylik_ozet([], 2026, 10)
    assert ozet.toplam == Decimal("0.00")
    assert ozet.adet == 0
    assert ozet.ortalama == Decimal("0.00")
    assert ozet.en_yuksek is None
    assert ozet.kategori_toplamlari == {}


def test_toplam_ortalama_en_yuksek():
    liste = [
        g(date(2026, 10, 1), "1000", "Maaş"),
        g(date(2026, 10, 15), "500.50", "Freelance"),
        g(date(2026, 10, 20), "250", "Freelance"),
    ]
    ozet = aylik_ozet(liste, 2026, 10)
    assert ozet.toplam == Decimal("1750.50")
    assert ozet.adet == 3
    assert ozet.ortalama == Decimal("583.50")
    assert ozet.en_yuksek.tutar == Decimal("1000.00")


def test_baska_aylarin_kayitlari_sayilmaz():
    liste = [g(date(2026, 9, 30), "999"), g(date(2026, 10, 1), "100"), g(date(2025, 10, 1), "999")]
    assert aylik_ozet(liste, 2026, 10).toplam == Decimal("100.00")


def test_kategori_toplamlari_buyukten_kucuge():
    liste = [
        g(date(2026, 10, 1), "100", "B"),
        g(date(2026, 10, 2), "300", "A"),
        g(date(2026, 10, 3), "200", "B"),
    ]
    ozet = aylik_ozet(liste, 2026, 10)
    assert list(ozet.kategori_toplamlari.items()) == [("A", Decimal("300.00")), ("B", Decimal("300.00"))]


def test_kategori_esitlikte_isme_gore_sirali():
    liste = [g(date(2026, 10, 1), "100", "Z"), g(date(2026, 10, 2), "100", "A")]
    assert list(aylik_ozet(liste, 2026, 10).kategori_toplamlari) == ["A", "Z"]


def test_ortalama_yuvarlama():
    liste = [g(date(2026, 10, 1), "10"), g(date(2026, 10, 2), "10"), g(date(2026, 10, 3), "10.01")]
    assert aylik_ozet(liste, 2026, 10).ortalama == Decimal("10.00")


def test_ay_gecisleri():
    assert onceki_ay(2026, 1) == (2025, 12)
    assert onceki_ay(2026, 10) == (2026, 9)
    assert sonraki_ay(2026, 12) == (2027, 1)
    assert sonraki_ay(2026, 10) == (2026, 11)


# ---- Karşılaştırma -----------------------------------------------------------

def test_karsilastir_artis_ve_dusus():
    onceki = aylik_ozet([g(date(2026, 9, 1), "1000")], 2026, 9)
    artis = karsilastir(aylik_ozet([g(date(2026, 10, 1), "1250")], 2026, 10), onceki)
    assert artis.fark == Decimal("250.00")
    assert artis.yuzde_degisim == Decimal("25.0")
    dusus = karsilastir(aylik_ozet([g(date(2026, 10, 1), "900")], 2026, 10), onceki)
    assert dusus.fark == Decimal("-100.00")
    assert dusus.yuzde_degisim == Decimal("-10.0")


def test_karsilastir_onceki_ay_bossa_yuzde_yok():
    bos = aylik_ozet([], 2026, 9)
    sonuc = karsilastir(aylik_ozet([g(date(2026, 10, 1), "500")], 2026, 10), bos)
    assert sonuc.fark == Decimal("500.00")
    assert sonuc.yuzde_degisim is None


def test_degisim_onceki_negatifse_yuzde_yok():
    sonuc = degisim(Decimal("100"), Decimal("-50"))
    assert sonuc.fark == Decimal("150")
    assert sonuc.yuzde_degisim is None


# ---- Bütçe: maaş + ek gelir - gider = kalan ------------------------------------

def test_butce_maas_ek_gelir_ve_giderden_kalan():
    maas = Maas(2026, 8, "30000")
    gelirler = [g(date(2026, 10, 12), "4750")]
    giderler = [gider(date(2026, 10, 1), "12000", "Kira"), gider(date(2026, 10, 8), "4200")]
    b = butce_hesapla(maas, gelirler, giderler, 2026, 10)
    assert b.maas == Decimal("30000.00")
    assert b.ek_gelir.toplam == Decimal("4750.00")
    assert b.gider.toplam == Decimal("16200.00")
    assert b.toplam_gelir == Decimal("34750.00")
    assert b.kalan == Decimal("18550.00")
    assert b.harcama_orani == Decimal("46.6")  # 16200 / 34750


def test_butce_maas_girilmemisse_sifir_sayilir():
    b = butce_hesapla(None, [], [gider(date(2026, 10, 1), "500")], 2026, 10)
    assert b.maas == Decimal("0.00")
    assert b.kalan == Decimal("-500.00")
    assert b.harcama_orani is None  # gelir yok: oran anlamsız


def test_butce_giderler_maasi_asarsa_kalan_negatif():
    b = butce_hesapla(Maas(2026, 10, "1000"), [], [gider(date(2026, 10, 2), "1500")], 2026, 10)
    assert b.kalan == Decimal("-500.00")
    assert b.harcama_orani == Decimal("150.0")


def test_butce_baska_ayin_kayitlari_karismaz():
    giderler = [gider(date(2026, 9, 30), "999"), gider(date(2026, 10, 1), "100")]
    b = butce_hesapla(Maas(2026, 1, "1000"), [], giderler, 2026, 10)
    assert b.gider.toplam == Decimal("100.00")
    assert b.kalan == Decimal("900.00")


# ---- Servis uçtan uca ----------------------------------------------------------

def yeni_servis():
    return ButceServisi(depo=Depo(":memory:"))


def test_servis_rapor_maas_tasinir_ve_giderler_dusulur():
    s = yeni_servis()
    s.maas_ayarla(2026, 8, "30000")
    s.kayit_ekle("gider", date(2026, 9, 5), "10000", "Kira")
    s.kayit_ekle("gider", date(2026, 10, 5), "12000", "Kira", "zamlı")
    s.kayit_ekle("gelir", date(2026, 10, 12), "500", "Freelance")
    rapor = s.aylik_rapor(2026, 10)
    assert rapor.maas == Maas(2026, 8, "30000")  # Ağustos'tan beri geçerli
    assert rapor.butce.kalan == Decimal("18500.00")
    assert [h.tur for h in rapor.hareketler] == ["gelir", "gider"]  # tarihe göre yeniden eskiye
    # önceki ay (Eylül): 30000 - 10000 = 20000 -> bu ay 18500: fark -1500, %-7,5
    assert rapor.kalan_karsilastirma.onceki_toplam == Decimal("20000.00")
    assert rapor.kalan_karsilastirma.fark == Decimal("-1500.00")
    assert rapor.kalan_karsilastirma.yuzde_degisim == Decimal("-7.5")
    s.kapat()


def test_servis_zam_sadece_o_aydan_itibaren():
    s = yeni_servis()
    s.maas_ayarla(2026, 1, "30000")
    s.maas_ayarla(2026, 10, "35000")
    assert s.aylik_rapor(2026, 9).butce.maas == Decimal("30000.00")
    assert s.aylik_rapor(2026, 10).butce.maas == Decimal("35000.00")
    assert s.aylik_rapor(2027, 2).butce.maas == Decimal("35000.00")
    assert s.aylik_rapor(2025, 12).maas is None
    s.kapat()


def test_servis_ocak_icin_onceki_yil_aralik():
    s = yeni_servis()
    s.maas_ayarla(2025, 1, "1000")
    s.kayit_ekle("gider", date(2025, 12, 31), "100", "Market")
    s.kayit_ekle("gider", date(2026, 1, 1), "150", "Market")
    k = s.aylik_rapor(2026, 1).kalan_karsilastirma
    assert k.onceki_toplam == Decimal("900.00")
    s.kapat()


def test_servis_kayit_guncelle_ve_sil():
    s = yeni_servis()
    kayit = s.kayit_ekle("gider", date(2026, 10, 3), "100", "Market")
    assert s.kayit_guncelle("gider", kayit.id, date(2026, 10, 4), "250,5".replace(",", "."), "Fatura", "su") is True
    degisen = s.kayit_getir("gider", kayit.id)
    assert (degisen.tarih, degisen.tutar, degisen.kategori, degisen.aciklama) == (
        date(2026, 10, 4), Decimal("250.50"), "Fatura", "su")
    assert s.kayit_sil("gider", kayit.id) is True
    assert s.kayit_getir("gider", kayit.id) is None
    s.kapat()


def test_servis_gecersiz_kayit_hata_verir_ve_kaydetmez():
    s = yeni_servis()
    try:
        s.kayit_ekle("gider", date(2026, 10, 3), "-5", "Market")
    except ValueError:
        pass
    else:
        raise AssertionError("ValueError bekleniyordu")
    assert s.tum_kayitlar("gider") == []
    s.kapat()


def test_servis_kategoriler_tur_basina_varsayilan_ve_ozel_tekrarsiz():
    s = yeni_servis()
    s.kayit_ekle("gider", date(2026, 10, 1), "10", "Evcil Hayvan")
    s.kayit_ekle("gider", date(2026, 10, 2), "10", "market")  # varsayılanın küçük harfli hali
    kategoriler = s.kategoriler("gider")
    assert "Evcil Hayvan" in kategoriler
    assert [k.casefold() for k in kategoriler].count("market") == 1
    assert "Freelance" not in kategoriler
    assert "Freelance" in s.kategoriler("gelir")
    s.kapat()


# ---- Kategori payları -----------------------------------------------------------

def test_kategori_paylari_yuzde_ve_siralama():
    liste = [
        gider(date(2026, 10, 1), "12000", "Kira"),
        gider(date(2026, 10, 2), "4200", "Market"),
        gider(date(2026, 10, 3), "900", "Ulaşım"),
        gider(date(2026, 10, 4), "900", "Market"),
    ]
    paylar = kategori_paylari(aylik_ozet(liste, 2026, 10))  # toplam 18000
    assert [(p.kategori, p.tutar, p.yuzde) for p in paylar] == [
        ("Kira", Decimal("12000.00"), Decimal("66.7")),
        ("Market", Decimal("5100.00"), Decimal("28.3")),   # 4200 + 900 birleşir
        ("Ulaşım", Decimal("900.00"), Decimal("5.0")),
    ]


def test_kategori_paylari_bos_ay_bos_liste():
    assert kategori_paylari(aylik_ozet([], 2026, 10)) == []


def test_kategori_paylari_en_fazla_ile_gruplar():
    liste = [gider(date(2026, 10, 1), tutar, ad) for ad, tutar in
             (("A", "500"), ("B", "300"), ("C", "100"), ("D", "60"), ("E", "40"))]
    paylar = kategori_paylari(aylik_ozet(liste, 2026, 10), en_fazla=3)
    assert [p.kategori for p in paylar] == ["A", "B", DIGER_KATEGORILER]
    assert paylar[2].tutar == Decimal("200.00")      # C + D + E
    assert paylar[2].yuzde == Decimal("20.0")
    assert sum(p.tutar for p in paylar) == Decimal("1000.00")


def test_kategori_paylari_en_fazla_yeterliyse_gruplamaz():
    liste = [gider(date(2026, 10, 1), "100", "A"), gider(date(2026, 10, 2), "100", "B")]
    assert [p.kategori for p in kategori_paylari(aylik_ozet(liste, 2026, 10), en_fazla=2)] == ["A", "B"]


# ---- Servis: genişletilmiş rapor ve toplu silme -----------------------------------

def test_rapor_gider_karsilastirmasi_ve_onceki_butce():
    s = yeni_servis()
    s.maas_ayarla(2026, 1, "10000")
    s.kayit_ekle("gider", date(2026, 9, 5), "2000", "Market")
    s.kayit_ekle("gider", date(2026, 10, 5), "2500", "Market")
    r = s.aylik_rapor(2026, 10)
    assert r.onceki_veri_var is True
    assert r.onceki_butce.kalan == Decimal("8000.00")
    assert r.gider_karsilastirma.fark == Decimal("500.00")
    assert r.gider_karsilastirma.yuzde_degisim == Decimal("25.0")
    s.kapat()


def test_rapor_onceki_ay_bossa_veri_yok_isaretlenir():
    s = yeni_servis()
    s.kayit_ekle("gider", date(2026, 10, 5), "100", "Market")
    assert s.aylik_rapor(2026, 10).onceki_veri_var is False
    s.maas_ayarla(2026, 9, "1000")  # önceki ayda maaş tanımlıysa karşılaştırma anlamlı
    assert s.aylik_rapor(2026, 10).onceki_veri_var is True
    s.kapat()


def test_servis_tum_verileri_sil():
    s = yeni_servis()
    s.maas_ayarla(2026, 1, "1000")
    s.kayit_ekle("gider", date(2026, 10, 5), "100", "Market")
    s.kayit_ekle("gelir", date(2026, 10, 6), "50", "Freelance")
    assert s.veri_sayilari().toplam == 3
    silinen = s.tum_verileri_sil()
    assert (silinen.gider, silinen.gelir, silinen.maas) == (1, 1, 1)
    assert s.veri_sayilari().toplam == 0
    rapor = s.aylik_rapor(2026, 10)
    assert rapor.hareketler == [] and rapor.maas is None and rapor.butce.kalan == Decimal("0.00")
    s.kapat()
