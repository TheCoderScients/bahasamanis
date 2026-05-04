# Roadmap Proyek Besar Bahasa Manis

Dokumen ini adalah checklist panjang untuk mengarahkan Bahasa Manis dari bahasa belajar
menjadi bahasa yang layak dipakai pada proyek besar secara bertahap.

## Definisi Siap Proyek Besar

Bahasa Manis dianggap siap untuk proyek besar jika:

- [ ] Struktur proyek standar jelas dan konsisten.
- [ ] Konfigurasi proyek punya format stabil.
- [ ] CLI mendukung siklus kerja harian: buat, jalankan, cek, tes, bangun, rilis.
- [ ] Error message membantu pemula dan tetap cukup detail untuk developer lanjut.
- [ ] Modul dan package bisa dipakai di banyak file tanpa path manual yang rapuh.
- [ ] Standard library cukup untuk aplikasi umum: file, JSON, HTTP, database, log, env, waktu, CSV.
- [ ] Testing punya pola yang jelas, bukan hanya menjalankan script biasa.
- [ ] Tooling editor mendukung highlight, snippet, dan nanti language server.
- [ ] Dokumentasi punya panduan pemula, panduan proyek, panduan produksi, dan contoh nyata.
- [ ] Kompatibilitas dijaga dengan SemVer dan catatan deprecation.

## Fase 0: Fondasi Bahasa

- [x] Interpreter menjalankan file `.bm`.
- [x] Transpiler mengubah `.bm` ke Python.
- [x] CLI dasar tersedia: `bm jalankan`, `bm ubah`, `bm interaktif`, `bm versi`.
- [x] Sintaks Indonesia inti tersedia: `jika`, `lain jika`, `selama`, `setiap`, `ulangi`, `fungsi`.
- [x] Builtin Indonesia inti tersedia: `panjang`, `angka`, `pecahan`, `teks`, `daftar`, `kamus`.
- [x] OOP dasar tersedia: `kelas`, `ini`, `mulai`.
- [x] Exception handling tersedia: `coba`, `tangkap`, `akhirnya`, `lempar`.
- [x] Async dasar tersedia: `asinkron`, `tunggu`, `jeda`.
- [x] Mode aman playground tersedia.
- [x] Test interpreter, transpiler, CLI, server, dan mode aman tersedia.

## Fase 1: Workflow Proyek

- [x] `bm buat nama_proyek` membuat struktur proyek awal.
- [x] Scaffold punya `src/`, `tests/`, `bm.toml`, `README.md`, dan `.gitignore`.
- [x] `bm cek` memvalidasi file `.bm`.
- [x] `bm tes` menjalankan test `.bm`.
- [x] `bm diagnosa` menampilkan lokasi command, Python, dan modul.
- [x] `bm jalankan` memberi exit code gagal saat runtime error.
- [x] `bm.toml` mulai dipakai oleh CLI.
- [x] `bm info` menampilkan konfigurasi proyek.
- [x] `bm jalankan` tanpa file memakai `utama` dari `bm.toml`.
- [x] Folder biasa tanpa `bm.toml` tetap bisa memakai `bm info`, `bm cek`, `bm tes`, dan `bm jalankan`.
- [x] `bm ubah` punya output default berbasis `bm.toml`.
- [x] `bm cek` punya mode ketat untuk CI.
- [x] `bm tes` punya ringkasan test yang lebih rapi.
- [x] `bm bersih` menghapus cache dan hasil build.

## Fase 2: Package dan Modul

- [x] Format `bm.toml` distabilkan.
- [x] Field proyek wajib dan opsional terdokumentasi.
- [ ] `pakai` mendukung import relatif proyek secara konsisten.
- [ ] `pakai` mendukung folder modul.
- [ ] Namespace package ditentukan.
- [ ] Resolusi modul punya pesan error yang jelas.
- [ ] `bm paket` menampilkan dependency dan modul proyek.
- [ ] Mekanisme dependency lokal dirancang.
- [ ] Mekanisme dependency publik dirancang setelah 1.0 stabil.

## Fase 3: Standard Library Produksi

- [x] Modul standar JSON tersedia.
- [x] Modul standar waktu tersedia.
- [x] Helper file tersedia.
- [x] Modul standar acak tersedia.
- [x] Modul `env` untuk membaca environment variable.
- [x] Modul `log` untuk logging sederhana.
- [x] Modul `csv` untuk data tabel.
- [ ] Modul `sqlite` untuk database lokal.
- [ ] Modul `http` untuk request HTTP sederhana.
- [ ] Modul `argumen` untuk CLI app.
- [ ] Modul `proses` untuk menjalankan command dengan aman.
- [ ] Dokumentasi tiap modul standar punya contoh.

## Fase 4: Quality Tools

- [ ] `bm format` untuk format kode otomatis.
- [ ] `bm cek` mendeteksi sintaks berisiko, bukan hanya parse error.
- [ ] Pesan warning punya saran perbaikan.
- [ ] Test BM punya helper `pastikan`.
- [ ] Test BM punya helper `sama`, `tidak_sama`, `benar`, `salah`.
- [ ] CI template tersedia.
- [ ] Coverage atau laporan file test dirancang.
- [ ] Error output punya format stabil untuk editor dan CI.

## Fase 5: Build dan Deploy

- [x] `bm bangun` membuat output Python dari proyek.
- [x] `bm bangun` membaca `utama` dari `bm.toml`.
- [x] Output build punya folder standar.
- [ ] Template Docker untuk CLI app tersedia.
- [ ] Template web API sederhana tersedia.
- [ ] Release checklist untuk PyPI tersedia.
- [ ] Artifact build bisa dites otomatis.
- [ ] Dokumentasi deploy server sederhana tersedia.

## Fase 6: Editor dan Developer Experience

- [x] VS Code syntax highlighting tersedia.
- [x] VS Code snippets tersedia.
- [ ] Snippet disesuaikan dengan workflow proyek.
- [ ] Formatter bisa dipanggil dari editor.
- [ ] Linter bisa dipanggil dari editor.
- [ ] Language server dirancang.
- [ ] Go to definition untuk fungsi dan modul dirancang.
- [ ] Hover docs untuk builtin dirancang.

## Fase 7: Dokumentasi dan Contoh Nyata

- [x] README menjelaskan instalasi dan quickstart.
- [x] Panduan pemula tersedia.
- [x] Roadmap stabilisasi tersedia.
- [x] Roadmap proyek besar tersedia.
- [ ] Panduan membuat CLI app tersedia.
- [ ] Panduan membuat automation tool tersedia.
- [ ] Panduan membuat web API tersedia.
- [ ] Contoh proyek besar mini tersedia.
- [ ] Tutorial testing Bahasa Manis tersedia.
- [x] Dokumentasi `bm.toml` lengkap tersedia.

## Fase 8: Keamanan, Stabilitas, dan Performa

- [x] Playground punya mode aman.
- [x] Playground punya timeout worker.
- [ ] Sandbox punya working directory sementara per run.
- [ ] Batas ukuran output terdokumentasi.
- [ ] Batas waktu eksekusi CLI untuk CI dirancang.
- [ ] Benchmark awal interpreter tersedia.
- [ ] Regression test untuk bug penting tersedia.
- [ ] Kebijakan kompatibilitas 1.0 ditulis jelas.

## Fase 9: Rilis 1.0 dan Setelahnya

- [ ] Semua fitur 1.0 diberi label stabil atau eksperimental.
- [ ] Breaking change terakhir diselesaikan sebelum 1.0.
- [ ] Deprecation policy ditulis.
- [ ] Changelog 1.0 lengkap.
- [ ] Tag GitHub 1.0 dibuat.
- [ ] Paket PyPI 1.0 dirilis.
- [ ] Roadmap 1.1 dibuat setelah 1.0.

## Prioritas Terdekat

Urutan kerja paling masuk akal dari kondisi sekarang:

1. Tambah `bm paket` untuk melihat modul/dependency proyek.
2. Tambah helper test `pastikan`.
3. Buat contoh proyek besar mini.
4. Siapkan rilis `1.0.0-rc.1`.
