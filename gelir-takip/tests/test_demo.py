from datetime import date
from decimal import Decimal

import pytest

from gelir_takip.db import Depo
from gelir_takip.demo import ornek_veri_ekle
from gelir_takip.servis import ButceServisi


@pytest.mark.parametrize("bugun", [date(2026, 10, 4), date(2026, 1, 31), date(2026, 3, 1), date(2024, 2, 29)])
def test_ornek_veri_maas_gider_ve_ek_gelir(bugun):
    servis = ButceServisi(depo=Depo(":memory:"))
    ornek_veri_ekle(servis, bugun)
    rapor = servis.aylik_rapor(bugun.year, bugun.month)
    butce = rapor.butce
    assert butce.maas == Decimal("32500.00")          # bu ay zamlı maaş
    assert butce.ek_gelir.toplam == Decimal("4750.00")
    assert butce.gider.adet == 5
    assert butce.gider.toplam == Decimal("19600.00")
    assert butce.kalan == Decimal("17650.00")
    assert len(rapor.hareketler) == 6
    # önceki ay eski maaşıyla: 30000 + 2500 - 18500 = 14000
    assert rapor.kalan_karsilastirma.onceki_toplam == Decimal("14000.00")
    assert rapor.kalan_karsilastirma.fark == Decimal("3650.00")
    assert rapor.kalan_karsilastirma.yuzde_degisim == Decimal("26.1")
    servis.kapat()
