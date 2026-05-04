# Panduan Pemula Bahasa Manis

Panduan ini untuk orang yang baru belajar ngoding dan ingin mulai dari Bahasa Indonesia.

## 1. Instalasi

Jika ingin memakai CLI langsung:

```bash
pipx install bahasamanis
```

Untuk pengembangan dari source:

```bash
pip install -e ".[dev,web]"
```

Cek versi:

```bash
bm versi
```

Kalau perintah `bm` sudah ada tetapi gagal karena `bahasamanis_cli` tidak ditemukan,
pasang ulang dari folder source Bahasa Manis:

```bash
python -m pip install --force-reinstall -e .
bm diagnosa
```

## 2. Program Pertama

Buat file `halo.bm`:

```bm
cetak "Halo, Indonesia!"
```

Jalankan:

```bash
bm jalankan halo.bm
```

## 3. Membuat Proyek

Kalau ingin mulai dengan struktur yang lebih rapi:

```bash
bm buat aplikasi_saya
cd aplikasi_saya
bm info
bm jalankan
bm cek
bm cek --ketat
bm tes
bm ubah
bm bangun
bm paket
bm bersih
```

`bm cek` memeriksa file `.bm` tanpa menjalankan program.
`bm cek --ketat` cocok untuk CI karena warning gaya sederhana ikut dianggap gagal.
`bm tes` menjalankan file test `.bm` di folder `tests`.
`bm jalankan` otomatis membaca file utama dari `bm.toml` kalau dijalankan dari folder proyek.
`bm ubah` otomatis membuat output Python di `build/utama.py` untuk proyek baru.
`bm bangun` mengecek proyek lalu membuat hasil Python yang bisa dijalankan.
`bm paket` menampilkan modul BM dan paket Python yang dipakai proyek.
`bm bersih` menghapus cache dan hasil build.

Kalau folder kamu belum punya `bm.toml`, tetap bisa dipakai:

```bash
bm info
bm cek
bm paket
bm jalankan nama_file.bm
```

Jika folder hanya punya satu file `.bm`, `bm jalankan` bisa langsung menebak file itu.

## 4. Input

```bm
tanya Nama kamu: sebagai nama
cetak "Halo, {nama}!"
```

`tanya` cocok untuk pemula karena prompt dan input jadi satu baris.
Untuk prompt teks biasa, tanda kutip boleh dihilangkan.

## 5. Percabangan

```bm
tanya "Nilai: " sebagai nilai
nilai = angka(nilai)

jika nilai >= 75
    cetak "Lulus"
lain
    cetak "Belum lulus"
akhir
```

Untuk banyak pilihan menu, gunakan `pilih`:

```bm
tanya "Pilih menu: " sebagai menu

pilih menu
    saat "1"
        cetak "Tambah data"
    saat "2"
        cetak "Lihat data"
    bawaan
        cetak "Menu tidak tersedia"
akhir
```

## 6. Loop

Untuk mengulang sejumlah kali:

```bm
ulangi 3 kali lakukan
    cetak "Belajar Bahasa Manis"
akhir
```

Untuk membaca isi daftar:

```bm
nama = ["Sari", "Budi", "Ayu"]

setiap item dalam nama
    cetak "Halo, {item}"
akhir
```

## 7. Fungsi

```bm
fungsi salam(nama)
    kembali "Halo, {nama}"
akhir

cetak salam("BM")
```

## 8. Data

Daftar:

```bm
buah = daftar()
tambah(buah, "apel")
tambah(buah, "jeruk")
cetak gabung(buah, ", ")
```

Kamus:

```bm
profil = kamus()
atur(profil, "nama", "Ayu")
atur(profil, "kelas", "XI")
cetak ambil(profil, "nama")
```

## 9. Berkas

Untuk aplikasi lokal:

```bm
path = "catatan.txt"
tulis_berkas(path, "Belajar Bahasa Manis\n")
tambah_berkas(path, "Hari ini menyenangkan")
cetak baca_berkas(path)
```

Catatan: helper berkas dimatikan di mode aman playground publik.

## 10. Modul Standar Ringkas

Untuk fitur yang sering dipakai di aplikasi, gunakan modul standar:

```bm
pakai "bm_standar/env" sebagai env
pakai "bm_standar/log" sebagai log
pakai "bm_standar/csv" sebagai csv

log.atur("INFO")
log.info("Aplikasi dimulai")

mode = env.ambil("MODE", "dev")
cetak "Mode: {mode}"

data = [{"nama": "Ayu", "nilai": "90"}]
cetak csv.bentuk(data, ["nama", "nilai"])
```

Modul yang tersedia sekarang antara lain `json`, `berkas`, `waktu`, `acak`,
`jaringan`, `env`, `log`, dan `csv`.

## 11. Mini Project: Catatan Sederhana

```bm
path = "catatan.txt"

cetak "=== Catatan ==="
cetak "1. Tambah catatan"
cetak "2. Lihat catatan"
tanya "Pilih: " sebagai menu

pilih menu
    saat "1"
        tanya "Isi catatan: " sebagai isi
        tambah_berkas(path, "{isi}\n")
        cetak "Catatan disimpan."
    saat "2"
        jika ada_berkas(path) maka
            cetak baca_berkas(path)
        lain
            cetak "Belum ada catatan."
        akhir
    bawaan
        cetak "Menu tidak tersedia."
akhir
```

Kalau fungsi tidak punya parameter, tanda kurung boleh dihilangkan:

```bm
fungsi halo
    kembali "Halo!"
akhir
```

## 12. Lanjut Belajar

Setelah menguasai dasar:

- Baca `examples/`.
- Coba `bm interaktif`.
- Pelajari `coba/tangkap` untuk menangani error.
- Pelajari `kelas` dan `asinkron` setelah dasar sudah kuat.
