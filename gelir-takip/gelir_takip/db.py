"""Veri katmanı: gelir kayıtlarının SQLite'ta saklanması.

Tutarlar kayan noktalı sayı hatası olmasın diye kuruş cinsinden tamsayı saklanır.
"""

from __future__ import annotations

import sqlite3
from datetime import date
from decimal import Decimal
from pathlib import Path

from .models import Gelir

_SEMA = """
CREATE TABLE IF NOT EXISTS gelir (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    tarih       TEXT    NOT NULL,            -- ISO: YYYY-MM-DD
    tutar_kurus INTEGER NOT NULL CHECK (tutar_kurus > 0),
    kategori    TEXT    NOT NULL,
    aciklama    TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_gelir_tarih ON gelir (tarih);
"""


def varsayilan_db_yolu() -> Path:
    """Kullanıcının ev klasöründe: ~/.gelir_takip/gelir.db"""
    return Path.home() / ".gelir_takip" / "gelir.db"


def _satirdan_gelire(satir: sqlite3.Row) -> Gelir:
    return Gelir(
        id=satir["id"],
        tarih=date.fromisoformat(satir["tarih"]),
        tutar=Decimal(satir["tutar_kurus"]) / 100,
        kategori=satir["kategori"],
        aciklama=satir["aciklama"],
    )


def _kurus(tutar: Decimal) -> int:
    return int(tutar * 100)


class GelirDeposu:
    """Gelir kayıtları için ekle / getir / güncelle / sil / listele."""

    def __init__(self, yol: str | Path = ":memory:") -> None:
        if str(yol) != ":memory:":
            Path(yol).parent.mkdir(parents=True, exist_ok=True)
        self._baglanti = sqlite3.connect(str(yol))
        self._baglanti.row_factory = sqlite3.Row
        self._baglanti.executescript(_SEMA)

    def kapat(self) -> None:
        self._baglanti.close()

    def ekle(self, gelir: Gelir) -> Gelir:
        """Kaydı ekler; id atanmış yeni bir Gelir döndürür."""
        with self._baglanti:
            imle = self._baglanti.execute(
                "INSERT INTO gelir (tarih, tutar_kurus, kategori, aciklama) VALUES (?, ?, ?, ?)",
                (gelir.tarih.isoformat(), _kurus(gelir.tutar), gelir.kategori, gelir.aciklama),
            )
        return Gelir(
            id=imle.lastrowid,
            tarih=gelir.tarih,
            tutar=gelir.tutar,
            kategori=gelir.kategori,
            aciklama=gelir.aciklama,
        )

    def getir(self, gelir_id: int) -> Gelir | None:
        satir = self._baglanti.execute("SELECT * FROM gelir WHERE id = ?", (gelir_id,)).fetchone()
        return _satirdan_gelire(satir) if satir else None

    def guncelle(self, gelir: Gelir) -> bool:
        """id'si olan kaydı günceller. Kayıt yoksa False döner."""
        if gelir.id is None:
            raise ValueError("Güncellenecek kaydın id'si yok.")
        with self._baglanti:
            imle = self._baglanti.execute(
                "UPDATE gelir SET tarih = ?, tutar_kurus = ?, kategori = ?, aciklama = ? WHERE id = ?",
                (gelir.tarih.isoformat(), _kurus(gelir.tutar), gelir.kategori, gelir.aciklama, gelir.id),
            )
        return imle.rowcount > 0

    def sil(self, gelir_id: int) -> bool:
        with self._baglanti:
            imle = self._baglanti.execute("DELETE FROM gelir WHERE id = ?", (gelir_id,))
        return imle.rowcount > 0

    def ay_listele(self, yil: int, ay: int) -> list[Gelir]:
        """Verilen aydaki kayıtlar, en yeni tarih önce."""
        baslangic = date(yil, ay, 1)
        bitis = date(yil + 1, 1, 1) if ay == 12 else date(yil, ay + 1, 1)
        satirlar = self._baglanti.execute(
            "SELECT * FROM gelir WHERE tarih >= ? AND tarih < ? ORDER BY tarih DESC, id DESC",
            (baslangic.isoformat(), bitis.isoformat()),
        ).fetchall()
        return [_satirdan_gelire(s) for s in satirlar]

    def tumunu_listele(self) -> list[Gelir]:
        satirlar = self._baglanti.execute("SELECT * FROM gelir ORDER BY tarih DESC, id DESC").fetchall()
        return [_satirdan_gelire(s) for s in satirlar]

    def kullanilan_kategoriler(self) -> list[str]:
        satirlar = self._baglanti.execute(
            "SELECT DISTINCT kategori FROM gelir ORDER BY kategori COLLATE NOCASE"
        ).fetchall()
        return [s["kategori"] for s in satirlar]
