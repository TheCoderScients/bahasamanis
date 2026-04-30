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

## 2. Program Pertama

Buat file `halo.bm`:

```bm
cetak "Halo, Indonesia!"
```

Jalankan:

```bash
bm jalankan halo.bm
```

## 3. Input

```bm
tanya "Nama kamu: " sebagai nama
cetak "Halo, {nama}!"
```

`tanya` cocok untuk pemula karena prompt dan input jadi satu baris.

## 4. Percabangan

```bm
tanya "Nilai: " sebagai nilai
nilai = angka(nilai)

jika nilai >= 75 maka
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

## 5. Loop

Untuk mengulang sejumlah kali:

```bm
ulangi 3 kali lakukan
    cetak "Belajar Bahasa Manis"
akhir
```

Untuk membaca isi daftar:

```bm
nama = ["Sari", "Budi", "Ayu"]

setiap item dalam nama lakukan
    cetak "Halo, {item}"
akhir
```

## 6. Fungsi

```bm
fungsi salam(nama)
    kembali "Halo, {nama}"
akhir

cetak salam("BM")
```

## 7. Data

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

## 8. Berkas

Untuk aplikasi lokal:

```bm
path = "catatan.txt"
tulis_berkas(path, "Belajar Bahasa Manis\n")
tambah_berkas(path, "Hari ini menyenangkan")
cetak baca_berkas(path)
```

Catatan: helper berkas dimatikan di mode aman playground publik.

## 9. Mini Project: Catatan Sederhana

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

## 10. Lanjut Belajar

Setelah menguasai dasar:

- Baca `examples/`.
- Coba `bm interaktif`.
- Pelajari `coba/tangkap` untuk menangani error.
- Pelajari `kelas` dan `asinkron` setelah dasar sudah kuat.
