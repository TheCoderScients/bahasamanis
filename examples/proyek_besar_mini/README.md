# ManisMart Mini

Contoh proyek besar mini untuk Bahasa Manis.

Proyek ini dibuat untuk menunjukkan pola kerja yang lebih rapi:

- `src/utama.bm` sebagai file utama.
- `src/domain/` untuk logika aplikasi.
- `tests/` untuk test otomatis Bahasa Manis.
- `bm.toml` untuk konfigurasi proyek.
- `data/` untuk contoh data aplikasi.

## Jalankan

```bash
bm info
bm jalankan
bm cek
bm tes
bm paket
bm bangun
python build/utama.py
```

## Yang Dipelajari

- Memecah aplikasi ke beberapa modul dengan `pakai`.
- Memakai helper test seperti `pastikan_sama`.
- Memakai modul standar `bm_standar/csv`.
- Menjaga proyek tetap bisa dicek, dites, dan dibangun.

