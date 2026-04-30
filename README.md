# Bahasa Manis (BM)

<p align="center">
  <img src="https://raw.githubusercontent.com/TheCoderScients/bahasamanis/main/vscode-bahasamanis/images/icon.png" alt="Bahasa Manis icon" width="128" />
</p>

[![PyPI version](https://img.shields.io/pypi/v/bahasamanis.svg)](https://pypi.org/project/bahasamanis/)

Bahasa pemrograman berbahasa Indonesia dengan interpreter, transpiler, CLI, dan playground web.

Status proyek: `0.2.0b1` beta stabilisasi. Bahasa Manis sudah enak untuk belajar, tugas, demo, dan aplikasi teks kecil. Jalur menuju rilis stabil ada di [docs/STABILITAS.md](docs/STABILITAS.md) dan [docs/ROADMAP.md](docs/ROADMAP.md).

PyPI: https://pypi.org/project/bahasamanis/

## Dokumentasi Penting

- [Panduan Pemula](docs/PANDUAN_PEMULA.md)
- [Roadmap](docs/ROADMAP.md)
- [Stabilitas](docs/STABILITAS.md)
- [Keamanan Playground](docs/KEAMANAN_PLAYGROUND.md)
- [QA Release](docs/QA_RELEASE.md)
- [Changelog](CHANGELOG.md)

## Instalasi

Disarankan menggunakan pipx (CLI terisolasi dan langsung tersedia di PATH):

```
pipx ensurepath
pipx install bahasamanis
```

Alternatif (pip + virtualenv):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install bahasamanis
```

Instalasi dari sumber (pengembangan):

```
pip install -e ".[dev,web]"
python -m pytest
```

Perintah CLI:

- `bm jalankan file.bm`
- `bm ubah file.bm -o file.py`
- `bm interaktif`

Alias lama tetap tersedia untuk kompatibilitas: `run`, `transpile`, dan `repl`.

## Playground Web

```
python server.py
# buka http://127.0.0.1:5000
```

Playground memakai mode aman secara default: `paket`, `pakai`, dan akses berkas dimatikan supaya lebih aman untuk publik. Untuk eksperimen lokal yang butuh akses penuh:

```
BM_PLAYGROUND_UNSAFE=1 python server.py
```

Jangan aktifkan mode unsafe untuk playground publik.

## Quickstart Pemula

```
cetak "Masukkan nama:"
baca nama

jika panjang(nama) == 0 maka
    cetak "Halo, teman!"
lain
    cetak "Halo, {nama}!"
akhir
```

Jalankan:

```
bm jalankan hello.bm
```

## Fitur Bahasa Singkat

- Kata kunci: `cetak`, `baca`, `tanya`, `jika/lain jika/lain/akhir`, `pilih/saat/bawaan`, `selama`, `untuk/setiap`, `ulangi`, `fungsi/kembali`, `lanjut/lanjutkan`, `henti/berhenti`, `lewati`
- Boolean: `benar`, `salah`
- Operator logika: `dan`, `atau`, `tidak`
- Komentar: baris penuh atau komentar inline dengan `#`
- Interpolasi string: `"Halo, {nama}"` (ekspresi di dalam `{...}` aman & didukung)
- Alias lama `elif` masih bisa dipakai, tetapi untuk kode baru disarankan `lain jika`.

## Fungsi Dasar Berbahasa Indonesia

Untuk pemula, Bahasa Manis menyediakan nama fungsi yang terasa lebih lokal:

| Bahasa Manis | Padanan Python | Contoh |
| --- | --- | --- |
| `panjang(data)` | `len(data)` | `panjang(nama)` |
| `angka(teks)` | `int(teks)` | `angka("12")` |
| `pecahan(teks)` | `float(teks)` | `pecahan("3.5")` |
| `teks(nilai)` | `str(nilai)` | `teks(2026)` |
| `rentang(awal, akhir)` | `range(...)` | `rentang(1, 5)` |
| `bulatkan(nilai)` | `round(nilai)` | `bulatkan(3.14)` |
| `rapikan(teks)` | `teks.strip()` | `rapikan(nama)` |
| `kecil(teks)` | `teks.lower()` | `kecil("HALO")` |
| `besar(teks)` | `teks.upper()` | `besar("halo")` |
| `ganti(teks, lama, baru)` | `teks.replace(...)` | `ganti(kata, "a", "i")` |
| `pisah(teks, pemisah)` | `teks.split(...)` | `pisah("a,b", ",")` |
| `gabung(data, pemisah)` | `pemisah.join(data)` | `gabung(["a","b"], ", ")` |
| `tambah(daftar, nilai)` | `daftar.append(nilai)` | `tambah(daftar, "Budi")` |
| `daftar(data)` | `list(data)` | `daftar("abc")` |
| `kamus()` | `dict()` | `profil = kamus()` |
| `berisi(data, nilai)` | `nilai in data` | `berisi(nama, "Budi")` |
| `ambil(data, kunci, bawaan)` | `data.get(...)` / indeks | `ambil(profil, "kelas", "-")` |
| `atur(data, kunci, nilai)` | set item | `atur(profil, "kelas", "XI")` |
| `hapus(data, nilai)` | remove/pop | `hapus(nama, "Budi")` |
| `urutkan(data)` | `sorted(data)` | `urutkan(nilai)` |
| `balik(data)` | reversed copy | `balik(nama)` |
| `baca_berkas(path)` | baca teks file | `baca_berkas("data.txt")` |
| `baca_baris(path)` | baca file jadi daftar baris | `baca_baris("data.txt")` |
| `tulis_berkas(path, isi)` | tulis teks file | `tulis_berkas("data.txt", "Halo")` |
| `tambah_berkas(path, isi)` | tambah teks ke file | `tambah_berkas("data.txt", "Halo")` |
| `ada_berkas(path)` | cek file/folder ada | `ada_berkas("data.txt")` |
| `hapus_berkas(path)` | hapus file | `hapus_berkas("data.txt")` |
| `daftar_berkas(path)` | daftar nama file/folder | `daftar_berkas(".")` |

Loop daftar bisa ditulis lebih natural:

```bm
nama = ["Sari", "Budi", "Ayu"]

untuk item dalam nama lakukan
    cetak "Halo, {item}"
akhir
```

Alias yang lebih santai juga tersedia:

```bm
setiap item dalam nama lakukan
    cetak item
akhir
```

Untuk mengulang sejumlah kali:

```bm
ulangi 3 kali lakukan
    cetak "Belajar Bahasa Manis"
akhir
```

Untuk mengecek isi data:

```bm
jika "Sari" dalam nama maka
    cetak "Sari ditemukan"
akhir
```

Kontrol loop bisa ditulis jelas:

```bm
untuk item dalam nama lakukan
    jika item == "Budi" maka
        lanjutkan
    akhir

    cetak item

    jika item == "Ayu" maka
        berhenti
    akhir
akhir
```

Untuk blok yang sengaja dikosongkan dulu, pakai `lewati`:

```bm
jika benar maka
    lewati
akhir
```

Loop `selama` juga bisa memakai kata `lakukan`:

```bm
jumlah = 0

selama jumlah < 3 lakukan
    jumlah = jumlah + 1
akhir
```

Input dengan prompt bisa ditulis singkat:

```bm
tanya "Masukkan nama: " sebagai nama
cetak "Halo, {nama}!"
```

Untuk menu, pakai `pilih` agar tidak terlalu banyak `lain jika`:

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

Untuk aplikasi kecil yang perlu menyimpan data:

```bm
path = "catatan.txt"

tulis_berkas(path, "Belajar BM\n")
tambah_berkas(path, "Data kedua")

jika ada_berkas(path) maka
    cetak baca_berkas(path)
akhir
```

Contoh percabangan yang disarankan:

```bm
cetak "Masukkan nilai:"
baca nilai
nilai = angka(nilai)

jika nilai >= 90 maka
    cetak "Sangat baik"
lain jika nilai >= 75 maka
    cetak "Baik"
lain
    cetak "Perlu latihan lagi"
akhir
```

## Fitur Lanjutan

Bahasa Manis juga punya subset fitur lanjutan yang tetap dibuat sederhana.

### Menangani Kesalahan

```bm
coba
    nilai = angka("abc")
tangkap error
    cetak "Input tidak valid"
    cetak error
akhirnya
    cetak "Selesai dicek"
akhir
```

Kamu juga bisa membuat kesalahan sendiri:

```bm
lempar "Data tidak boleh kosong"
```

Alias `gagal "pesan"` juga tersedia.

### Kelas dan Objek

Gunakan `kelas` untuk membuat objek. Fungsi `mulai` berjalan saat objek dibuat, dan `ini` berarti objek saat ini.

```bm
kelas Siswa
    fungsi mulai(nama, nilai)
        ini.nama = nama
        ini.nilai = nilai
    akhir

    fungsi info()
        kembali "{ini.nama}: {ini.nilai}"
    akhir
akhir

s = Siswa("Budi", 88)
cetak s.info()
```

### Asinkron

Gunakan `asinkron fungsi`, `tunggu`, dan `jeda` untuk pekerjaan yang perlu menunggu tanpa memblokir gaya penulisan program.

```bm
asinkron fungsi ambil_pesan(nama)
    tunggu jeda(1)
    kembali "Halo, {nama}"
akhir

pesan = tunggu ambil_pesan("BM")
cetak pesan
```

## Interop Python & Modul BM (paket/pakai)

- Impor modul Python dengan alias Indonesia:

  ```bm
  paket "math" sebagai m
  cetak "akar 16 = {m.sqrt(16)}"
  ```

- Impor modul BM lokal atau pustaka standar berbahasa Indonesia:

  ```bm
  pakai "bm_standar/json" sebagai j
  data = {"nama": "BM", "versi": 1}
  cetak j.bentuk(data, rapi=benar)
  ```

Catatan: Paket `bahasamanis` menyertakan data paket `bahasamanis_data` yang berisi folder `bm_standar/`, sehingga contoh di atas berfungsi langsung setelah instal dari PyPI (tanpa perlu menyalin file .bm secara manual).

## Pustaka Standar BM

Paket `bahasamanis` menyertakan pustaka standar BM yang dapat diimpor menggunakan perintah `pakai`. Pustaka standar ini termasuk:

- `bm_standar/json`: modul untuk bekerja dengan data JSON
- `bm_standar/jaringan`: modul untuk bekerja dengan jaringan
- `bm_standar/waktu`: modul untuk bekerja dengan waktu
- `bm_standar/acak`: modul untuk bekerja dengan bilangan acak

## Transpile -> Python

String dengan `{...}` ditranspilasi menjadi f-string Python.

```
# BM
cetak "Halo, {1+2}"

# Python
print(f"Halo, {1+2}")
```

## Error Berbahasa Indonesia

Pesan kesalahan telah dilokalkan, misalnya:

- `Kesalahan sintaks pada ekspresi ...: tidak ditutup`
- `Kesalahan runtime pada baris N: operator '>' tidak didukung antara tipe 'str' dan 'int'`

## VS Code Extension (lokal)

Folder: `vscode-bahasamanis/`

Cara coba:

1. Buka folder `vscode-bahasamanis/` di VS Code.
2. Tekan `F5` untuk menjalankan Extension Development Host.
3. Buka file `.bm` untuk melihat highlight dan snippet.

## Windows EXE

Rilis menyediakan binary tunggal `bm.exe` di halaman Release GitHub. Unduh `bm.exe`, lalu jalankan:

```
bm.exe jalankan contoh.bm
```

## Changelog ringkas

### 0.2.0b1
- Sintaks Indonesia yang lebih ramah pemula: `lain jika` sebagai pengganti yang disarankan untuk `elif`.
- Fungsi dasar berbahasa Indonesia: `panjang`, `angka`, `pecahan`, `teks`, `rapikan`, `kecil`, `besar`, `ganti`, `pisah`, `gabung`, `tambah`, dan lainnya.
- Loop pemula: `untuk item dalam data lakukan`, `setiap item dalam data lakukan`, `selama kondisi lakukan`, `ulangi N kali lakukan`, dan operator `dalam`.
- Kontrol loop punya alias pemula: `henti/berhenti`, `lanjut/lanjutkan`, dan `lewati`.
- Input dan menu lebih ramah: `tanya "..." sebagai nama`, `pilih/saat/bawaan`.
- Helper berkas: `baca_berkas`, `baca_baris`, `tulis_berkas`, `tambah_berkas`, `ada_berkas`, `hapus_berkas`, dan `daftar_berkas`.
- Komentar inline `#` aman selama tidak berada di dalam string.
- Fitur lanjutan sederhana: `coba/tangkap/akhirnya`, `kelas` dengan `ini`, dan `asinkron fungsi` dengan `tunggu`.
- Mode aman untuk playground: import Python, import BM, dan akses berkas bisa dimatikan.
- CI diperkuat untuk Python 3.9 sampai 3.13.
- CLI Indonesia lebih jelas: `bm jalankan`, `bm ubah`, dan `bm interaktif`.
- Snippet dan highlight VS Code diperbarui mengikuti gaya Indonesia.

### 0.1.11
- Interop Python: `paket "modul" sebagai alias`
- Import modul BM: `pakai "path/modul.bm" [sebagai alias]`
- CLI Indonesia: `bm jalankan`, `bm ubah`, `bm repl` (kompatibel dengan `run`/`transpile`)
- Pustaka standar dibundel: `bm_standar/{berkas,json,jaringan,waktu,acak}` via paket data `bahasamanis_data`
- Perbaikan runtime: output `print` di-flush, resolusi `pakai` lebih kuat, default argumen fungsi dievaluasi saat pemanggilan

## Lisensi

MIT
