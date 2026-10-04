"""İş mantığı: aylık özet, bütçe (kalan) ve ay karşılaştırması. Saf fonksiyonlar, veritabanı bilmez."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

from .formatting import tr_siralama_anahtari
from .models import Kayit, Maas

_SIFIR = Decimal("0.00")


@dataclass(frozen=True)
class AylikOzet:
    yil: int
    ay: int
    toplam: Decimal = _SIFIR
    adet: int = 0
    ortalama: Decimal = _SIFIR
    en_yuksek: Kayit | None = None
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


def aylik_ozet(kayitlar: list[Kayit], yil: int, ay: int) -> AylikOzet:
    """Verilen listeden yalnızca (yil, ay) içindeki kayıtları özetler."""
    ay_gelirleri = [g for g in kayitlar if g.tarih.year == yil and g.tarih.month == ay]
    if not ay_gelirleri:
        return AylikOzet(yil=yil, ay=ay)

    toplam = sum((g.tutar for g in ay_gelirleri), _SIFIR)
    ortalama = (toplam / len(ay_gelirleri)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    kategoriler: dict[str, Decimal] = defaultdict(lambda: _SIFIR)
    for g in ay_gelirleri:
        kategoriler[g.kategori] += g.tutar
    sirali = dict(sorted(kategoriler.items(), key=lambda oge: (-oge[1], tr_siralama_anahtari(oge[0]))))

    return AylikOzet(
        yil=yil,
        ay=ay,
        toplam=toplam,
        adet=len(ay_gelirleri),
        ortalama=ortalama,
        en_yuksek=max(ay_gelirleri, key=lambda g: g.tutar),
        kategori_toplamlari=sirali,
    )


def degisim(simdiki: Decimal, onceki: Decimal) -> AyKarsilastirma:
    """İki tutar arasındaki fark ve yüzde değişim. Önceki tutar 0 ya da negatifse yüzde anlamsızdır (None)."""
    fark = simdiki - onceki
    if onceki <= 0:
        yuzde = None
    else:
        yuzde = (fark / onceki * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return AyKarsilastirma(onceki_toplam=onceki, fark=fark, yuzde_degisim=yuzde)


def karsilastir(bu_ay: AylikOzet, onceki: AylikOzet) -> AyKarsilastirma:
    return degisim(bu_ay.toplam, onceki.toplam)


@dataclass(frozen=True)
class AylikButce:
    """Bir ayın tam tablosu: maaş + ek gelir - gider = kalan."""

    yil: int
    ay: int
    maas: Decimal
    ek_gelir: AylikOzet
    gider: AylikOzet
    toplam_gelir: Decimal            # maaş + ek gelir
    kalan: Decimal                   # toplam gelir - gider (aşılırsa negatif)
    harcama_orani: Decimal | None    # gider / toplam gelir * 100; gelir yoksa None


def butce_hesapla(
    maas: Maas | None, gelirler: list[Kayit], giderler: list[Kayit], yil: int, ay: int
) -> AylikButce:
    """`maas`, bu ay için geçerli maaş kaydıdır (yoksa None: maaş girilmemiş sayılır)."""
    maas_tutari = maas.tutar if maas else _SIFIR
    ek_gelir = aylik_ozet(gelirler, yil, ay)
    gider = aylik_ozet(giderler, yil, ay)
    toplam_gelir = maas_tutari + ek_gelir.toplam
    harcama_orani = None
    if toplam_gelir > 0:
        harcama_orani = (gider.toplam / toplam_gelir * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return AylikButce(
        yil=yil,
        ay=ay,
        maas=maas_tutari,
        ek_gelir=ek_gelir,
        gider=gider,
        toplam_gelir=toplam_gelir,
        kalan=toplam_gelir - gider.toplam,
        harcama_orani=harcama_orani,
    )


DIGER_KATEGORILER = "Diğer kategoriler"


@dataclass(frozen=True)
class KategoriPayi:
    kategori: str
    tutar: Decimal
    yuzde: Decimal  # toplam içindeki pay (0-100, 1 basamak)


def kategori_paylari(ozet: AylikOzet, en_fazla: int | None = None) -> list[KategoriPayi]:
    """Kategorilerin toplam içindeki payı, en büyük önce.

    `en_fazla` verilirse ve kategori sayısı bunu aşarsa en küçükler tek bir
    'Diğer kategoriler' satırında toplanır (toplam satır sayısı en_fazla olur).
    Toplam sıfırsa boş liste döner.
    """
    if ozet.toplam <= 0:
        return []
    ogeler = list(ozet.kategori_toplamlari.items())
    if en_fazla is not None and len(ogeler) > en_fazla:
        geri_kalan = sum((tutar for _, tutar in ogeler[en_fazla - 1:]), _SIFIR)
        ogeler = ogeler[: en_fazla - 1] + [(DIGER_KATEGORILER, geri_kalan)]
    return [
        KategoriPayi(kategori, tutar, (tutar / ozet.toplam * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
        for kategori, tutar in ogeler
    ]
