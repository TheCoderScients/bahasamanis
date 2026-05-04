# Roadmap Bahasa Manis

Roadmap ini menjaga Bahasa Manis tetap realistis: kuat untuk belajar dan aplikasi kecil, tetapi tidak mengaku sebagai pengganti penuh Python.

Untuk checklist besar menuju proyek produksi, lihat [ROADMAP_PROYEK_BESAR.md](ROADMAP_PROYEK_BESAR.md).

## Prinsip

- Bahasa Indonesia dulu, istilah Inggris tetap boleh sebagai kompatibilitas.
- Mudah dibaca oleh pemula.
- Setiap fitur inti harus punya contoh dan test.
- Playground publik harus aman secara default.
- Stable berarti kompatibilitas dan keandalan, bukan jumlah fitur terbanyak.

## 0.2.0rc1

Tujuan: kandidat rilis stabil untuk fitur beta `0.2.x`.

Prioritas:

- Perbaiki pesan error yang paling sering dialami pemula.
- Lengkapi dokumentasi pemula dan mini project.
- Pastikan semua contoh penting masuk CI.
- Rapikan batas mode aman playground.
- Audit fitur eksperimental agar labelnya jelas.

Checklist:

- [x] Error `nama belum dibuat` lebih jelas untuk variabel yang belum ada.
- [x] Error blok belum ditutup memberi petunjuk `akhir`.
- [x] Error `angka("abc")` memberi konteks bahwa teks bukan angka.
- [x] Panduan pemula punya alur instalasi, input, percabangan, loop, fungsi, data, file, dan mini project.
- [x] Dokumen keamanan playground menjelaskan mode aman dan mode unsafe.
- [x] Playground menjalankan kode user di worker process dengan timeout.
- [x] Sintaks pemula dibuat lebih lentur tanpa mengganti gaya lama.
- [x] Workflow proyek awal tersedia lewat `bm buat`, `bm cek`, dan `bm tes`.
- [x] Checklist proyek besar tersedia di `docs/ROADMAP_PROYEK_BESAR.md`.
- [x] `bm.toml` mulai dipakai oleh CLI lewat `bm info` dan `bm jalankan` tanpa file.
- [x] Format `bm.toml` v1 terdokumentasi.
- [x] `bm bangun` membuat output Python dari proyek.
- [x] `bm paket` menampilkan modul BM dan paket Python yang dipakai proyek.
- [x] Modul standar `env`, `log`, dan `csv` tersedia.
- [x] Semua demo non-interaktif jalan lewat `examples/run_all_demos.bm`.
- [x] `python -m pytest` hijau.
- [x] Build paket dan `twine check` hijau.

Tidak masuk `0.2.0rc1`:

- Sistem package baru.
- OOP kompleks seperti inheritance.
- Async event loop lanjutan.
- Optimisasi performa besar.

## 1.0.0

Tujuan: rilis stabil publik.

Kriteria:

- Kontrak fitur inti tidak berubah tanpa deprecation.
- CLI stabil dan terdokumentasi.
- Test inti mencakup interpreter, transpiler, CLI, mode aman, dan contoh.
- README cukup jelas untuk orang yang baru belajar ngoding.
- Playground publik tidak membuka akses server.
- Changelog dan release notes jelas.

## Setelah 1.0.0

Ide yang boleh dieksplorasi setelah fondasi stabil:

- Formatter `.bm`.
- Linter pesan ramah pemula.
- Paket standar yang lebih kaya.
- Dokumentasi website khusus.
- Sandbox playground dengan batas memori dan working directory sementara.
