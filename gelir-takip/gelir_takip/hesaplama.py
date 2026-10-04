"""İş mantığı: aylık özet ve ay karşılaştırması. Saf fonksiyonlar, veritabanı bilmez."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

from .models import Gelir

_SIFIR = Decimal("0.00")


@dataclass(frozen=True)
class AylikOzet:
    yil: int
    ay: int
    toplam: Decimal = _SIFIR
    adet: int = 0
    ortalama: Decimal = _SIFIR
    en_yuksek: Gelir | None = None
    # kategori -> toplam, en büyük kategori önce
    kategori_toplamlari: dict[str, Decimal] = field(default_factory=dict)


@dataclass(frozen=True)
class AyKarsilastirma:
    onceki_toplam: Decimal
    fark: Decimal                      # bu ay - önceki ay
    yuzde_degisim: Decimal | None      # önceki ay 0 ise None


def onceki_ay(yil: int, ay: int) -> tuple[int, int]:
    return (yil - 1, 12) if ay == 1 else (yil, ay - 1)


def sonraki_ay(yil: int, ay: int) -> tuple[int, int]:
    return (yil + 1, 1) if ay == 12 else (yil, ay + 1)


def aylik_ozet(gelirler: list[Gelir], yil: int, ay: int) -> AylikOzet:
    """Verilen listeden yalnızca (yil, ay) içindeki kayıtları özetler."""
    ay_gelirleri = [g for g in gelirler if g.tarih.year == yil and g.tarih.month == ay]
    if not ay_gelirleri:
        return AylikOzet(yil=yil, ay=ay)

    toplam = sum((g.tutar for g in ay_gelirleri), _SIFIR)
    ortalama = (toplam / len(ay_gelirleri)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    kategoriler: dict[str, Decimal] = defaultdict(lambda: _SIFIR)
    for g in ay_gelirleri:
        kategoriler[g.kategori] += g.tutar
    sirali = dict(sorted(kategoriler.items(), key=lambda oge: (-oge[1], oge[0])))

    return AylikOzet(
        yil=yil,
        ay=ay,
        toplam=toplam,
        adet=len(ay_gelirleri),
        ortalama=ortalama,
        en_yuksek=max(ay_gelirleri, key=lambda g: g.tutar),
        kategori_toplamlari=sirali,
    )


def karsilastir(bu_ay: AylikOzet, onceki: AylikOzet) -> AyKarsilastirma:
    fark = bu_ay.toplam - onceki.toplam
    if onceki.toplam == 0:
        yuzde = None
    else:
        yuzde = (fark / onceki.toplam * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return AyKarsilastirma(onceki_toplam=onceki.toplam, fark=fark, yuzde_degisim=yuzde)
