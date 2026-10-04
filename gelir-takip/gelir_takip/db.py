"""Veri katmanı: gelir, gider ve maaş kayıtlarının SQLite'ta saklanması.

Tutarlar kayan noktalı sayı hatası olmasın diye kuruş cinsinden tamsayı saklanır.
Üç depo tek bir bağlantıyı paylaşır (bellek içi veritabanı için de gerekli).
"""

from __future__ import annotations

import sqlite3
from datetime import date
from decimal import Decimal
from pathlib import Path

from .models import KAYIT_SINIFLARI, TUR_GELIR, TUR_GIDER, Kayit, Maas, VeriSayilari

_KAYIT_TABLOSU = """
CREATE TABLE IF NOT EXISTS {tablo} (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    tarih       TEXT    NOT NULL,            -- ISO: YYYY-MM-DD
    tutar_kurus INTEGER NOT NULL CHECK (tutar_kurus > 0),
    kategori    TEXT    NOT NULL,
    aciklama    TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_{tablo}_tarih ON {tablo} (tarih);
"""

_MAAS_TABLOSU = """
CREATE TABLE IF NOT EXISTS maas (
    yil         INTEGER NOT NULL,
    ay          INTEGER NOT NULL CHECK (ay BETWEEN 1 AND 12),
    tutar_kurus INTEGER NOT NULL CHECK (tutar_kurus >= 0),
    PRIMARY KEY (yil, ay)                    -- bu aydan itibaren geçerli
);
"""


def varsayilan_db_yolu() -> Path:
    """Kullanıcının ev klasöründe: ~/.gelir_takip/gelir.db"""
    return Path.home() / ".gelir_takip" / "gelir.db"


def _kurus(tutar: Decimal) -> int:
    return int(tutar * 100)


def _tutar(kurus: int) -> Decimal:
    return Decimal(kurus) / 100


class KayitDeposu:
    """Tek bir tablodaki (gelir ya da gider) kayıtlar için ekle / getir / güncelle / sil / listele."""

    def __init__(self, baglanti: sqlite3.Connection, tablo: str, model: type[Kayit]) -> None:
        self._baglanti = baglanti
        self._tablo = tablo  # yalnızca bu modüldeki sabit tablo adları gelir; kullanıcı girdisi değil
        self._model = model

    def _kayda(self, satir: sqlite3.Row) -> Kayit:
        return self._model(
            id=satir["id"],
            tarih=date.fromisoformat(satir["tarih"]),
            tutar=_tutar(satir["tutar_kurus"]),
            kategori=satir["kategori"],
            aciklama=satir["aciklama"],
        )

    def ekle(self, kayit: Kayit) -> Kayit:
        """Kaydı ekler; id atanmış yeni bir kayıt döndürür."""
        with self._baglanti:
            imle = self._baglanti.execute(
                f"INSERT INTO {self._tablo} (tarih, tutar_kurus, kategori, aciklama) VALUES (?, ?, ?, ?)",
                (kayit.tarih.isoformat(), _kurus(kayit.tutar), kayit.kategori, kayit.aciklama),
            )
        return self._model(
            id=imle.lastrowid,
            tarih=kayit.tarih,
            tutar=kayit.tutar,
            kategori=kayit.kategori,
            aciklama=kayit.aciklama,
        )

    def getir(self, kayit_id: int) -> Kayit | None:
        satir = self._baglanti.execute(
            f"SELECT * FROM {self._tablo} WHERE id = ?", (kayit_id,)
        ).fetchone()
        return self._kayda(satir) if satir else None

    def guncelle(self, kayit: Kayit) -> bool:
        """id'si olan kaydı günceller. Kayıt yoksa False döner."""
        if kayit.id is None:
            raise ValueError("Güncellenecek kaydın id'si yok.")
        with self._baglanti:
            imle = self._baglanti.execute(
                f"UPDATE {self._tablo} SET tarih = ?, tutar_kurus = ?, kategori = ?, aciklama = ? WHERE id = ?",
                (kayit.tarih.isoformat(), _kurus(kayit.tutar), kayit.kategori, kayit.aciklama, kayit.id),
            )
        return imle.rowcount > 0

    def sil(self, kayit_id: int) -> bool:
        with self._baglanti:
            imle = self._baglanti.execute(f"DELETE FROM {self._tablo} WHERE id = ?", (kayit_id,))
        return imle.rowcount > 0

    def ay_listele(self, yil: int, ay: int) -> list[Kayit]:
        """Verilen aydaki kayıtlar, en yeni tarih önce."""
        baslangic = date(yil, ay, 1)
        bitis = date(yil + 1, 1, 1) if ay == 12 else date(yil, ay + 1, 1)
        satirlar = self._baglanti.execute(
            f"SELECT * FROM {self._tablo} WHERE tarih >= ? AND tarih < ? ORDER BY tarih DESC, id DESC",
            (baslangic.isoformat(), bitis.isoformat()),
        ).fetchall()
        return [self._kayda(s) for s in satirlar]

    def tumunu_listele(self) -> list[Kayit]:
        satirlar = self._baglanti.execute(
            f"SELECT * FROM {self._tablo} ORDER BY tarih DESC, id DESC"
        ).fetchall()
        return [self._kayda(s) for s in satirlar]

    def kullanilan_kategoriler(self) -> list[str]:
        satirlar = self._baglanti.execute(
            f"SELECT DISTINCT kategori FROM {self._tablo} ORDER BY kategori COLLATE NOCASE"
        ).fetchall()
        return [s["kategori"] for s in satirlar]


class MaasDeposu:
    """Maaş geçmişi: her kayıt 'şu aydan itibaren geçerli' demektir."""

    def __init__(self, baglanti: sqlite3.Connection) -> None:
        self._baglanti = baglanti

    def ayarla(self, yil: int, ay: int, tutar: Decimal | str | float) -> Maas:
        """(yil, ay) ayından itibaren geçerli maaşı kaydeder; o ayda kayıt varsa üzerine yazar."""
        maas = Maas(yil=yil, ay=ay, tutar=tutar)  # doğrular
        with self._baglanti:
            self._baglanti.execute(
                "INSERT OR REPLACE INTO maas (yil, ay, tutar_kurus) VALUES (?, ?, ?)",
                (maas.yil, maas.ay, _kurus(maas.tutar)),
            )
        return maas

    def gecerli(self, yil: int, ay: int) -> Maas | None:
        """(yil, ay) için geçerli maaş: o aya veya daha öncesine ait en son kayıt. Yoksa None."""
        satir = self._baglanti.execute(
            "SELECT * FROM maas WHERE yil * 100 + ay <= ? ORDER BY yil DESC, ay DESC LIMIT 1",
            (yil * 100 + ay,),
        ).fetchone()
        if satir is None:
            return None
        return Maas(yil=satir["yil"], ay=satir["ay"], tutar=_tutar(satir["tutar_kurus"]))

    def sil(self, yil: int, ay: int) -> bool:
        """Tam bu aydan başlayan kaydı siler (önceki maaş yeniden geçerli olur)."""
        with self._baglanti:
            imle = self._baglanti.execute("DELETE FROM maas WHERE yil = ? AND ay = ?", (yil, ay))
        return imle.rowcount > 0

    def tumu(self) -> list[Maas]:
        """Tüm maaş kayıtları, eskiden yeniye."""
        satirlar = self._baglanti.execute("SELECT * FROM maas ORDER BY yil, ay").fetchall()
        return [Maas(yil=s["yil"], ay=s["ay"], tutar=_tutar(s["tutar_kurus"])) for s in satirlar]


class Depo:
    """Veritabanı bağlantısı ve üç depo: gelirler, giderler, maaslar."""

    def __init__(self, yol: str | Path = ":memory:") -> None:
        if str(yol) != ":memory:":
            Path(yol).parent.mkdir(parents=True, exist_ok=True)
        self._baglanti = sqlite3.connect(str(yol))
        self._baglanti.row_factory = sqlite3.Row
        self._baglanti.executescript(
            _KAYIT_TABLOSU.format(tablo="gelir") + _KAYIT_TABLOSU.format(tablo="gider") + _MAAS_TABLOSU
        )
        self.gelirler = KayitDeposu(self._baglanti, "gelir", KAYIT_SINIFLARI[TUR_GELIR])
        self.giderler = KayitDeposu(self._baglanti, "gider", KAYIT_SINIFLARI[TUR_GIDER])
        self.maaslar = MaasDeposu(self._baglanti)

    def kayitlar(self, tur: str) -> KayitDeposu:
        """'gelir' ya da 'gider' için ilgili depo."""
        return {TUR_GELIR: self.gelirler, TUR_GIDER: self.giderler}[tur]

    def sayilar(self) -> VeriSayilari:
        def say(tablo: str) -> int:
            return self._baglanti.execute(f"SELECT COUNT(*) FROM {tablo}").fetchone()[0]

        return VeriSayilari(gelir=say("gelir"), gider=say("gider"), maas=say("maas"))

    def hepsini_sil(self) -> VeriSayilari:
        """Tüm gelir, gider ve maaş kayıtlarını TEK işlemde siler (ya hepsi gider ya hiçbiri).

        Silinen kayıtların adetlerini döndürür. Geri alınamaz.
        """
        silinen = self.sayilar()
        with self._baglanti:
            for tablo in ("gelir", "gider", "maas"):
                self._baglanti.execute(f"DELETE FROM {tablo}")
        return silinen

    def kapat(self) -> None:
        self._baglanti.close()
