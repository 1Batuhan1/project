from datetime import date
from decimal import Decimal

import pytest

from gelir_takip.db import GelirDeposu
from gelir_takip.demo import ornek_veri_ekle
from gelir_takip.servis import GelirServisi


@pytest.mark.parametrize("bugun", [date(2026, 10, 4), date(2026, 1, 31), date(2026, 3, 1), date(2024, 2, 29)])
def test_ornek_veri_bu_ay_ve_onceki_aya_eklenir(bugun):
    servis = GelirServisi(depo=GelirDeposu(":memory:"))
    ornek_veri_ekle(servis, bugun)
    rapor = servis.aylik_rapor(bugun.year, bugun.month)
    assert rapor.ozet.adet == 5
    assert rapor.ozet.toplam == Decimal("47334.56")
    assert rapor.karsilastirma.onceki_toplam == Decimal("40500.00")
    servis.kapat()
