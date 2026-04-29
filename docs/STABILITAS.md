# Stabilitas Bahasa Manis

Dokumen ini menjelaskan arah Bahasa Manis menuju rilis stabil.

## Status Saat Ini

Versi saat ini: `0.2.0b1`.

Status: beta menuju stabil. Bahasa Manis sudah cocok untuk belajar, tugas, demo, dan aplikasi teks kecil. Rilis `1.0.0` hanya layak diberi label stabil setelah kontrak fitur, test, dokumentasi, dan keamanan playground terpenuhi.

## Kontrak Fitur Stabil

Fitur berikut dianggap inti dan harus dijaga kompatibilitasnya:

- Output dan input: `cetak`, `baca`, `tanya`
- Percabangan: `jika`, `lain jika`, `lain`, `pilih`, `saat`, `bawaan`
- Loop: `selama`, `untuk`, `setiap`, `ulangi`
- Kontrol loop: `henti`, `berhenti`, `lanjut`, `lanjutkan`, `lewati`
- Fungsi: `fungsi`, `kembali`, argumen default sederhana
- Data dasar: daftar, kamus, string, angka, boolean, `kosong`
- Helper Indonesia: `panjang`, `angka`, `pecahan`, `teks`, `rapikan`, `besar`, `kecil`, `tambah`, `ambil`, `atur`, dan keluarga helper data lain
- Penanganan kesalahan: `coba`, `tangkap`, `akhirnya`, `lempar`, `gagal`
- CLI: `bm jalankan`, `bm ubah`, `bm interaktif`

## Fitur Kuat Tapi Perlu Dijaga

Fitur berikut tetap didukung, tetapi harus dipakai hati-hati terutama di lingkungan publik:

- `paket` untuk import Python
- `pakai` untuk import modul BM lokal
- Helper berkas: `baca_berkas`, `tulis_berkas`, `hapus_berkas`, dan sejenisnya
- OOP sederhana: `kelas`, `mulai`, `ini`
- Asinkron sederhana: `asinkron fungsi`, `tunggu`, `jeda`

## Mode Aman

Interpreter punya mode aman:

```python
from bahasamanis import Interpreter

it = Interpreter(aman=True)
it.run('cetak "Halo dari mode aman"')
```

Di mode aman:

- `paket` dimatikan
- `pakai` dimatikan
- helper baca/tulis/hapus berkas dimatikan
- fitur dasar bahasa tetap bisa dipakai

Playground web lokal memakai mode aman secara default. Untuk eksperimen lokal yang memang butuh akses penuh, jalankan server dengan:

```bash
BM_PLAYGROUND_UNSAFE=1 python server.py
```

Jangan aktifkan mode unsafe untuk playground publik.

## Kriteria Rilis 1.0.0

Sebelum merilis `1.0.0`, pastikan:

- `python -m pytest` lulus
- CI lulus di Python 3.9 sampai 3.13
- `bm jalankan examples/run_all_demos.bm` lulus
- dokumentasi pemula sudah lengkap dan tidak menjanjikan fitur di luar implementasi
- playground publik memakai mode aman
- fitur eksperimental diberi label jelas
- changelog dan versi rilis sudah disiapkan

## Jalur Rilis yang Disarankan

- `0.2.0b1`: beta stabilisasi fitur Indonesia
- `0.2.0rc1`: release candidate setelah bugfix dan dokumentasi
- `1.0.0`: stabil jika CI, demo, docs, dan mode aman sudah siap
