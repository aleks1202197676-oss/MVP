from __future__ import annotations
# Заглушка: импорт Samsung Health экспорта (ZIP/CSV) -> staged -> mart
# Идея: поддержать 'drop folder', где появляется новый экспорт.
# Дальше: нормализуем таймзоны/форматы, пишем parquet/csv, строим агрегаты.
import os, glob, shutil, datetime as dt

def main(inbox="data/raw/health/inbox", out="data/outputs/latest/health"):
    os.makedirs(inbox, exist_ok=True)
    os.makedirs(out, exist_ok=True)
    exports = sorted(glob.glob(os.path.join(inbox, "*")))
    if not exports:
        print("[health] inbox пуст. Положи сюда экспорт Samsung Health (ZIP/CSV).")
        return
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    marker = os.path.join(out, f"import_marker_{ts}.txt")
    with open(marker, "w", encoding="utf-8") as f:
        f.write("Imported files:\n" + "\n".join(exports))
    print(f"[health] ok: {len(exports)} file(s) -> {marker}")

if __name__ == "__main__":
    main()
