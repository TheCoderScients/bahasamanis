# Bahasa Manis – VS Code Extension

Sintaks highlight + snippet untuk bahasa pemrograman Bahasa Manis (.bm).

CLI Bahasa Manis tersedia di PyPI: https://pypi.org/project/bahasamanis/

## Fitur
- Highlight keyword BM (`cetak`, `baca`, `tanya`, `jika/lain jika/lain/akhir`, `pilih/saat/bawaan`, `selama`, `untuk`, `setiap`, `fungsi`, `kelas`, `coba`, `asinkron`, `berhenti`, `lanjutkan`, `lewati`, dll.)
- Highlight string/angka/komentar
- Snippet bawaan: cetak, baca, tanya, jika-lain jika-lain, pilih, selama, untuk, untuk-dalam, setiap, ulangi, fungsi, kelas, coba/tangkap, asinkron, baca/tulis berkas, berhenti, lanjutkan, lewati
- Highlight fungsi dasar pemula seperti `panjang`, `angka`, `rapikan`, `kecil`, `tambah`, dan `baca_berkas`

## Instalasi
- Install dari Marketplace (jika sudah dipublikasikan), atau
- Install lokal dari file VSIX:
  1. Jalankan `vsce package` di folder `vscode-bahasamanis/`
  2. Di VS Code: Extensions → menu `...` → `Install from VSIX...`

CLI (opsional) — instal dari PyPI agar perintah `bm` tersedia:

```
pipx ensurepath
pipx install bahasamanis
```

## Cara Pakai
- Buka file berekstensi `.bm`
- Coba snippet:
  - Ketik `jika` lalu `Tab` → menghasilkan blok `jika/lain jika/lain/akhir`
  - Ketik `baca` lalu `Tab` → prompt input + `baca variabel`
  - Ketik `tanya` lalu `Tab` → input dengan prompt satu baris
  - Ketik `pilih` lalu `Tab` → percabangan menu
  - Ketik `untukdalam`, `setiap`, atau `ulangi` lalu `Tab` untuk loop pemula
  - Ketik `bacaberkas` atau `tulisberkas` lalu `Tab` untuk helper berkas
  - Ketik `kelas`, `coba`, atau `asinkron` lalu `Tab` untuk fitur lanjutan

## Ikon
Ikon di `images/icon.png`.

## Sumber Proyek
Bahasa Manis (BM): interpreter, transpiler, CLI, dan playground web.

PyPI: https://pypi.org/project/bahasamanis/
Repo: https://github.com/TheCoderScients/bahasamanis

Lisensi: MIT
