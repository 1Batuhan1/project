from datetime import date
from decimal import Decimal

import pytest

from gelir_takip.db import Depo
from gelir_takip.models import KAYIT_SINIFLARI, Maas


@pytest.fixture
def depo():
    d = Depo(":memory:")
    yield d
    d.kapat()


@pytest.fixture(params=["gelir", "gider"])
def tur(request):
    return request.param


def yeni(tur, tarih, tutar="100", kategori="Market", aciklama=""):
    return KAYIT_SINIFLARI[tur](tarih=tarih, tutar=tutar, kategori=kategori, aciklama=aciklama)


# ---- Gelir / gider kayıtları (iki tablo aynı şekilde davranır) -----------------

def test_ekle_ve_getir(depo, tur):
    kayitlar = depo.kayitlar(tur)
    kayit = kayitlar.ekle(yeni(tur, date(2026, 10, 4), "1234.56", "Freelance", "site işi"))
    assert kayit.id is not None
    okunan = kayitlar.getir(kayit.id)
    assert okunan == kayit
    assert okunan.tutar == Decimal("1234.56")
    assert type(okunan) is KAYIT_SINIFLARI[tur]


def test_gelir_ve_gider_tablolari_ayri(depo):
    depo.gelirler.ekle(yeni("gelir", date(2026, 10, 4)))
    assert depo.giderler.tumunu_listele() == []
    assert len(depo.gelirler.tumunu_listele()) == 1


def test_olmayan_kayit_none(depo, tur):
    assert depo.kayitlar(tur).getir(999) is None


def test_guncelle(depo, tur):
    kayitlar = depo.kayitlar(tur)
    kayit = kayitlar.ekle(yeni(tur, date(2026, 10, 4)))
    degisen = KAYIT_SINIFLARI[tur](id=kayit.id, tarih=date(2026, 10, 5), tutar="250.75", kategori="Ulaşım", aciklama="x")
    assert kayitlar.guncelle(degisen) is True
    assert kayitlar.getir(kayit.id) == degisen


def test_guncelle_olmayan_kayit_false(depo, tur):
    kayit = KAYIT_SINIFLARI[tur](id=42, tarih=date(2026, 1, 1), tutar=1, kategori="a")
    assert depo.kayitlar(tur).guncelle(kayit) is False


def test_guncelle_idsiz_hata(depo, tur):
    with pytest.raises(ValueError):
        depo.kayitlar(tur).guncelle(yeni(tur, date(2026, 1, 1)))


def test_sil(depo, tur):
    kayitlar = depo.kayitlar(tur)
    kayit = kayitlar.ekle(yeni(tur, date(2026, 10, 4)))
    assert kayitlar.sil(kayit.id) is True
    assert kayitlar.getir(kayit.id) is None
    assert kayitlar.sil(kayit.id) is False


def test_ay_listele_sinirlari_dogru(depo, tur):
    kayitlar = depo.kayitlar(tur)
    kayitlar.ekle(yeni(tur, date(2026, 9, 30)))   # önceki ay
    kayitlar.ekle(yeni(tur, date(2026, 10, 1)))   # ay başı (dahil)
    kayitlar.ekle(yeni(tur, date(2026, 10, 31)))  # ay sonu (dahil)
    kayitlar.ekle(yeni(tur, date(2026, 11, 1)))   # sonraki ay
    assert [k.tarih for k in kayitlar.ay_listele(2026, 10)] == [date(2026, 10, 31), date(2026, 10, 1)]


def test_ay_listele_aralik_yil_gecisi(depo, tur):
    kayitlar = depo.kayitlar(tur)
    kayitlar.ekle(yeni(tur, date(2026, 12, 31)))
    kayitlar.ekle(yeni(tur, date(2027, 1, 1)))
    assert [k.tarih for k in kayitlar.ay_listele(2026, 12)] == [date(2026, 12, 31)]


def test_kullanilan_kategoriler_tekrarsiz(depo, tur):
    kayitlar = depo.kayitlar(tur)
    kayitlar.ekle(yeni(tur, date(2026, 10, 1), kategori="Zeta"))
    kayitlar.ekle(yeni(tur, date(2026, 10, 2), kategori="alfa"))
    kayitlar.ekle(yeni(tur, date(2026, 10, 3), kategori="Zeta"))
    assert kayitlar.kullanilan_kategoriler() == ["alfa", "Zeta"]


# ---- Maaş geçmişi ---------------------------------------------------------------

def test_maas_yokken_none(depo):
    assert depo.maaslar.gecerli(2026, 10) is None


def test_maas_sonraki_aylara_tasinir_oncekilere_gecmez(depo):
    depo.maaslar.ayarla(2026, 8, "30000")
    assert depo.maaslar.gecerli(2026, 7) is None                       # öncesi: tanımsız
    assert depo.maaslar.gecerli(2026, 8).tutar == Decimal("30000.00")  # başladığı ay
    assert depo.maaslar.gecerli(2026, 12).tutar == Decimal("30000.00")  # yenisi girilene kadar taşınır
    assert depo.maaslar.gecerli(2027, 3).tutar == Decimal("30000.00")   # yıl geçse de


def test_zam_gecmis_aylari_degistirmez(depo):
    depo.maaslar.ayarla(2026, 8, "30000")
    depo.maaslar.ayarla(2026, 10, "35000")
    assert depo.maaslar.gecerli(2026, 9).tutar == Decimal("30000.00")   # eski maaş
    assert depo.maaslar.gecerli(2026, 10).tutar == Decimal("35000.00")
    assert depo.maaslar.gecerli(2027, 1).tutar == Decimal("35000.00")


def test_gecmise_maas_girmek_sonraki_zammi_bozmaz(depo):
    depo.maaslar.ayarla(2026, 12, "60000")
    depo.maaslar.ayarla(2026, 10, "50000")
    assert depo.maaslar.gecerli(2026, 11).tutar == Decimal("50000.00")
    assert depo.maaslar.gecerli(2026, 12).tutar == Decimal("60000.00")


def test_ayni_aya_maas_girmek_uzerine_yazar(depo):
    depo.maaslar.ayarla(2026, 10, "35000")
    depo.maaslar.ayarla(2026, 10, "36000")
    assert depo.maaslar.gecerli(2026, 10).tutar == Decimal("36000.00")
    assert len(depo.maaslar.tumu()) == 1


def test_maas_silinince_onceki_maas_gecerli_olur(depo):
    depo.maaslar.ayarla(2026, 8, "30000")
    depo.maaslar.ayarla(2026, 10, "35000")
    assert depo.maaslar.sil(2026, 10) is True
    assert depo.maaslar.gecerli(2026, 10).tutar == Decimal("30000.00")
    assert depo.maaslar.sil(2026, 10) is False


def test_maas_yil_gecisi(depo):
    depo.maaslar.ayarla(2025, 12, "100")
    assert depo.maaslar.gecerli(2026, 1).tutar == Decimal("100.00")


def test_maas_gecmisi_eskiden_yeniye(depo):
    depo.maaslar.ayarla(2026, 10, "2")
    depo.maaslar.ayarla(2025, 3, "1")
    assert depo.maaslar.tumu() == [Maas(2025, 3, "1"), Maas(2026, 10, "2")]


def test_gecersiz_maas_kaydedilmez(depo):
    with pytest.raises(ValueError):
        depo.maaslar.ayarla(2026, 13, "100")
    with pytest.raises(ValueError):
        depo.maaslar.ayarla(2026, 10, "-5")
    assert depo.maaslar.tumu() == []


def test_dosyaya_kalici_yazar(tmp_path):
    yol = tmp_path / "alt" / "gelir.db"
    d1 = Depo(yol)
    d1.giderler.ekle(yeni("gider", date(2026, 10, 4), "99.99"))
    d1.maaslar.ayarla(2026, 10, "5000")
    d1.kapat()
    d2 = Depo(yol)
    assert [g.tutar for g in d2.giderler.tumunu_listele()] == [Decimal("99.99")]
    assert d2.maaslar.gecerli(2026, 11).tutar == Decimal("5000.00")
    d2.kapat()
