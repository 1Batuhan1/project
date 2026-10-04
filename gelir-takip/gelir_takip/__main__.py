"""Uygulamayı başlatır:  python -m gelir_takip [--demo] [--db DOSYA]"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import date

from .db import Depo, varsayilan_db_yolu
from .demo import ornek_veri_ekle
from .servis import ButceServisi


def main(argv: list[str] | None = None) -> int:
    ayristirici = argparse.ArgumentParser(prog="gelir_takip", description="Aylık gelir takip uygulaması")
    ayristirici.add_argument("--db", help="Veritabanı dosyası (varsayılan: ~/.gelir_takip/gelir.db)")
    ayristirici.add_argument(
        "--demo",
        action="store_true",
        help="Örnek verilerle aç; hiçbir şey kaydedilmez (veriler bellekte tutulur)",
    )
    args = ayristirici.parse_args(argv)

    try:
        from .ui_tk.ana_pencere import calistir, hata_goster
    except ImportError as hata:
        print(f"Tkinter yüklenemedi: {hata}", file=sys.stderr)
        print("Linux'ta: sudo apt install python3-tk", file=sys.stderr)
        return 1

    if args.demo:
        servis = ButceServisi(depo=Depo(":memory:"))
        ornek_veri_ekle(servis, date.today())
    else:
        try:
            servis = ButceServisi(db_yolu=args.db)
        except (sqlite3.Error, OSError) as hata:
            mesaj = (
                f"Veritabanı açılamadı:\n{args.db or varsayilan_db_yolu()}\n\n{hata}\n\n"
                "Dosya bozuk olabilir, başka bir programda açık olabilir ya da klasöre yazma izniniz olmayabilir."
            )
            print(mesaj, file=sys.stderr)
            hata_goster("Gelir Takip", mesaj)
            return 1

    calistir(servis)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
