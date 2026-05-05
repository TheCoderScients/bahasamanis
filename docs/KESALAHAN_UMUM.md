# Kesalahan Umum dan Solusinya

Halaman ini membantu pengguna membedakan error kode, batasan fitur, dan cara
menulis proyek Bahasa Manis yang lebih aman.

## Kamus atau Daftar Multi-baris

Sekarang daftar dan kamus multi-baris didukung:

```bm
produk = {
    "kode": "BK-01",
    "nama": "Buku Tulis Premium",
    "harga": 12000,
    "stok": 35
}

keranjang = [
    {"kode": "BK-01", "jumlah": 2},
    {"kode": "PN-02", "jumlah": 5}
]
```

Jika lupa menutup `}`, `]`, atau `)`, `bm cek --ketat` akan memberi pesan
bahwa ekspresi multi-baris belum ditutup.

## Interpolasi String

Interpolasi `{nama}` bisa dipakai di banyak konteks:

```bm
nama = "Ayu"
baris = []

cetak "Halo, {nama}"
tambah(baris, "Pembeli: {nama}")

fungsi buat_pesan(total)
    kembali "Total: Rp{total}"
akhir
```

Jika ingin mencetak teks dengan kurung kurawal literal, pastikan isi di dalam
kurung bukan ekspresi Bahasa Manis yang valid, atau gandakan kurungnya:

```bm
cetak "Literal: {{nama}}"
```

## Variabel Global di Dalam Fungsi

Variabel level atas bisa dibaca dari fungsi:

```bm
PATH_DB = "data/db.json"

fungsi muat()
    kembali baca_berkas(PATH_DB)
akhir
```

Untuk proyek besar, tetap lebih rapi jika nilai penting dikirim sebagai
parameter saat fungsi mulai makin panjang.

## `bm cek --ketat`

Mode ketat sekarang memeriksa:

- blok yang belum ditutup dengan `akhir`
- daftar, kamus, atau argumen multi-baris yang belum ditutup
- ekspresi yang sintaksnya belum valid
- alias Inggris seperti `elif` dan `async`
- spasi kosong di akhir baris

Gunakan sebelum menjalankan atau commit:

```bash
bm format --cek
bm cek --ketat
bm tes
```

Jika `bm format --cek` gagal, jalankan `bm format` untuk merapikan indentasi
blok, spasi akhir, dan literal multi-baris.

## Program Interaktif

Jika program memakai `baca` atau `tanya`, menjalankan otomatis tanpa input bisa
berakhir dengan error EOF. Untuk proyek interaktif, siapkan test di folder
`tests/` supaya logika penting tetap bisa diuji tanpa mengetik menu manual.
