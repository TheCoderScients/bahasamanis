# Changelog

Semua perubahan penting Bahasa Manis dicatat di sini.

Format mengikuti gaya sederhana: fitur baru, perubahan, perbaikan, dan catatan keamanan.

## 0.2.0rc1 - Rencana

Fokus rilis ini adalah stabilisasi, bukan menambah banyak fitur baru.

Sudah dikerjakan:

- Error variabel belum dibuat sekarang memberi saran membuat variabel dengan assignment, `baca`, atau `tanya`.
- Error blok yang lupa `akhir` sekarang menyebut pembuka blok dan barisnya.
- `akhir`, `lain`, `saat`, `bawaan`, `tangkap`, dan `akhirnya` yang salah tempat sekarang memberi pesan konteks.
- `angka()` dan `pecahan()` sekarang memberi pesan Indonesia yang lebih ramah saat konversi gagal.
- Playground menjalankan kode user di worker process terpisah.
- Playground punya timeout eksekusi lewat `BM_PLAYGROUND_TIMEOUT_SECONDS`.
- Output playground dipotong dari dalam worker supaya lebih stabil.
- Sintaks pemula dibuat lebih lentur tanpa menghapus gaya lama: `maka/lakukan` bisa dihilangkan di beberapa blok.
- Fungsi tanpa parameter bisa ditulis `fungsi halo`.
- `cetak Halo dunia` dan `tanya Nama kamu: sebagai nama` bisa dipakai untuk teks biasa tanpa tanda kutip.
- CLI punya `bm diagnosa` untuk mengecek lokasi command, Python, dan modul yang sedang dipakai.
- CLI punya workflow proyek awal: `bm buat`, `bm cek`, dan `bm tes`.
- `bm jalankan` sekarang memberi exit code gagal saat runtime error terjadi.
- Roadmap proyek besar ditambahkan sebagai checklist lengkap.
- `bm.toml` mulai dipakai oleh CLI lewat `bm info` dan `bm jalankan` tanpa file.
- Folder biasa tanpa `bm.toml` tetap didukung oleh `bm info`, `bm cek`, `bm tes`, dan tebakan file utama untuk `bm jalankan`.
- `bm ubah` punya output default dari `bm.toml`, `bm cek --ketat` tersedia untuk CI, `bm tes` punya ringkasan, dan `bm bersih` menghapus cache/build.
- Format `bm.toml` v1 terdokumentasi dan divalidasi, serta `bm bangun` membuat output Python proyek dari file utama.
- Pustaka standar bertambah: `bm_standar/env`, `bm_standar/log`, `bm_standar/csv`, dan `bm_standar/uji`.
- CLI punya `bm paket` untuk melihat modul BM dan paket Python yang dipakai proyek.
- Helper test tersedia: `pastikan`, `pastikan_sama`/`sama`, `pastikan_tidak_sama`/`tidak_sama`, `pastikan_benar`, dan `pastikan_salah`.

Target utama:

- Error message makin jelas dan konsisten dalam Bahasa Indonesia.
- Dokumentasi pemula lebih runtut dari instalasi sampai mini project.
- Playground web tetap aman secara default dan terdokumentasi.
- Semua contoh di `examples/` jalan di CI.
- Test interpreter, transpiler, CLI, dan mode aman tetap hijau di Python 3.9 sampai 3.13.

Kriteria selesai:

- `python -m pytest` lulus.
- `bm jalankan examples/run_all_demos.bm` lulus.
- `python -m build && python -m twine check dist/*` lulus.
- Tidak ada fitur eksperimental yang dipromosikan sebagai stabil tanpa test.

## 0.2.0b1

Rilis beta stabilisasi pertama.

Fitur baru:

- Sintaks Indonesia yang lebih ramah pemula: `lain jika`, `tanya`, `pilih/saat/bawaan`, `setiap`, `ulangi`, `berhenti`, `lanjutkan`, dan `lewati`.
- Helper data berbahasa Indonesia seperti `panjang`, `angka`, `rapikan`, `tambah`, `ambil`, `atur`, `hapus`, `urutkan`, dan lainnya.
- Helper berkas: `baca_berkas`, `baca_baris`, `tulis_berkas`, `tambah_berkas`, `ada_berkas`, `hapus_berkas`, dan `daftar_berkas`.
- Fitur lanjutan sederhana: `coba/tangkap/akhirnya`, `kelas`, `ini`, `asinkron fungsi`, `tunggu`, dan `jeda`.
- Mode aman interpreter untuk playground publik.
- Perintah `bm versi` dan `bm --version`.

Perubahan:

- CLI Indonesia diprioritaskan: `bm jalankan`, `bm ubah`, dan `bm interaktif`.
- Alias lama `run`, `transpile`, dan `repl` tetap tersedia.
- Playground web sekarang membuat interpreter baru per request.
- CI diperkuat untuk Python 3.9 sampai 3.13.
- Workflow rilis menjalankan test sebelum publish.

Perbaikan:

- Keyword ekspresi tidak lagi mengubah isi string literal.
- Interpolasi string lebih aman.
- Nested block seperti `jika` di dalam `jika` ditangani lebih benar.
- Transpiler diperbarui mengikuti sintaks baru.
- Kompatibilitas Python 3.9 untuk CLI diperbaiki.

Keamanan:

- `paket`, `pakai`, dan helper berkas bisa dimatikan lewat `Interpreter(aman=True)`.
- Playground web memakai mode aman secara default.
- Akses eksplisit ke nama/atribut khusus Python seperti `__import__` diblok dari ekspresi BM.
