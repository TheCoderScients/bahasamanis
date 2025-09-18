# Bahasa Manis – VS Code Extension

Sintaks highlight + snippet untuk bahasa pemrograman Bahasa Manis (.bm).

## Fitur
- Highlight keyword BM (`cetak`, `baca`, `jika/elif/lain/akhir`, `selama`, `untuk`, `fungsi`, dll.)
- Highlight string/angka/komentar
- Snippet bawaan: cetak, baca, jika-elif-lain, selama, untuk, fungsi

## Instalasi
- Install dari Marketplace (jika sudah dipublikasikan), atau
- Install lokal dari file VSIX:
  1. Jalankan `vsce package` di folder `vscode-bahasamanis/`
  2. Di VS Code: Extensions → menu `...` → `Install from VSIX...`

## Cara Pakai
- Buka file berekstensi `.bm`
- Coba snippet:
  - Ketik `jika` lalu `Tab` → menghasilkan blok `jika/elif/lain/akhir`
  - Ketik `baca` lalu `Tab` → prompt input + `baca variabel`

## Ikon
Ikon di `images/icon.png`.

## Sumber Proyek
Bahasa Manis (BM): interpreter, transpiler, CLI, dan playground web.

Lisensi: MIT
