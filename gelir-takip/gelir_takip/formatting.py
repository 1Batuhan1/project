"""Türkçe biçimlendirme ve kullanıcı girdisini ayrıştırma yardımcıları."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

AY_ADLARI = (
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
)

_BINLIK_NOKTALI = re.compile(r"^\d{1,3}(\.\d{3})+$")
_BINLIK_VIRGULLU = re.compile(r"^\d{1,3}(,\d{3}){2,}$")  # tek virgül ondalık sayılır, en az iki grup şart


def ay_adi(ay: int) -> str:
    return AY_ADLARI[ay - 1]


def ay_etiketi(yil: int, ay: int) -> str:
    """(2026, 10) -> 'Ekim 2026'"""
    return f"{ay_adi(ay)} {yil}"


def para_bicimle(tutar: Decimal) -> str:
    """Decimal('1234.5') -> '1.234,50 ₺'; negatifse '−500,00 ₺' (gerçek eksi işaretiyle)."""
    tutar = Decimal(tutar).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    metin = f"{abs(tutar):,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{'−' if tutar < 0 else ''}{metin} ₺"


def oran_bicimle(oran: Decimal) -> str:
    """Decimal('52.6') -> '%52,6'"""
    return f"%{oran:.1f}".replace(".", ",")


def yuzde_bicimle(oran: Decimal | None) -> str:
    """Değişim oranı, işaretli: Decimal('12.5') -> '+%12,5'; Decimal('-3') -> '−%3,0'; None -> '—'"""
    if oran is None:
        return "—"
    isaret = "−" if oran < 0 else "+"
    return f"{isaret}{oran_bicimle(abs(oran))}"


def para_ayristir(metin: str) -> Decimal:
    """Kullanıcının yazdığı tutarı Decimal'e çevirir.

    Kabul edilenler: '1.234,56' (TR), '1,234.56' (US), '1234,56', '1234.56', '1.234',
    '1,234,567', '₺ 500', '500 TL'. Hem nokta hem virgül varsa SON görülen ayraç ondalıktır.
    Belirsiz ya da hatalı girişte (sayı değil, 2'den fazla ondalık basamak) ValueError fırlatır;
    tutarı sessizce yanlış okumaktansa kullanıcıya düzeltme şansı verilir.
    """
    temiz = (metin or "").replace("₺", "").replace("TL", "").replace("tl", "")
    temiz = temiz.replace(" ", "").strip()
    if not temiz:
        raise ValueError("Tutar boş olamaz.")

    if "," in temiz and "." in temiz:
        if temiz.rfind(",") > temiz.rfind("."):   # 1.234,56
            temiz = temiz.replace(".", "").replace(",", ".")
        else:                                       # 1,234.56
            temiz = temiz.replace(",", "")
    elif "," in temiz:
        if _BINLIK_VIRGULLU.match(temiz):           # 1,234,567
            temiz = temiz.replace(",", "")
        else:                                       # 12,5
            temiz = temiz.replace(",", ".")
    elif _BINLIK_NOKTALI.match(temiz):              # 1.234.567
        temiz = temiz.replace(".", "")

    try:
        tutar = Decimal(temiz)
    except InvalidOperation:
        raise ValueError("Tutar sayı olmalıdır.") from None
    if not tutar.is_finite():
        raise ValueError("Tutar sayı olmalıdır.")
    if tutar.as_tuple().exponent < -2:
        raise ValueError("Tutarda en fazla 2 ondalık basamak olabilir (örn. 1.234,56).")
    return tutar


def tarih_bicimle(tarih: date) -> str:
    return tarih.strftime("%d.%m.%Y")


def tarih_ayristir(metin: str) -> date:
    """'04.10.2026', '04/10/2026', '04-10-2026' veya '2026-10-04' -> date. Geçersizse ValueError."""
    metin = (metin or "").strip()
    for bicim in ("%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(metin, bicim).date()
        except ValueError:
            continue
    raise ValueError("Tarih GG.AA.YYYY biçiminde olmalıdır.")


_TR_ALFABE = "abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_TR_SIRA = {harf: sira + 1000 for sira, harf in enumerate(_TR_ALFABE)}


def tr_siralama_anahtari(metin: str) -> tuple[int, ...]:
    """Türkçe alfabe sırasına göre sıralama anahtarı (... c ç d ... g ğ h ı i ... o ö ... s ş t u ü v ...).

    Büyük/küçük harf fark etmez; rakam ve boşluk harflerden önce gelir.
    Python'un varsayılan sıralaması Ç, Ğ, İ, Ö, Ş, Ü'yü z'den sonraya atar.
    """
    kucuk = (metin or "").replace("I", "ı").replace("İ", "i").lower()
    return tuple(_TR_SIRA.get(harf, ord(harf)) for harf in kucuk)
