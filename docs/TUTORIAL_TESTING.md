# Tutorial Testing Bahasa Manis

Testing dipakai untuk memastikan perubahan kode tidak merusak fitur lama.

## Struktur Proyek

Proyek yang dibuat dengan `bm buat` sudah punya folder test:

```text
aplikasi_saya/
  bm.toml
  src/
    utama.bm
  tests/
    tes_utama.bm
```

Jalankan:

```bash
bm tes
```

## Test Paling Sederhana

```bm
fungsi tambah(a, b)
    kembali a + b
akhir

pastikan_sama(tambah(2, 3), 5, "Tambah harus menghasilkan 5")
cetak "Tes tambah lulus"
```

Simpan sebagai:

```text
tests/tes_utama.bm
```

## Helper Test

Helper yang tersedia:

| Helper | Kegunaan |
| --- | --- |
| `pastikan(kondisi, pesan)` | Kondisi umum harus benar |
| `pastikan_sama(a, b, pesan)` / `sama(a, b)` | Dua nilai harus sama |
| `pastikan_tidak_sama(a, b, pesan)` / `tidak_sama(a, b)` | Dua nilai harus berbeda |
| `pastikan_benar(nilai, pesan)` | Nilai harus benar |
| `pastikan_salah(nilai, pesan)` | Nilai harus salah |

Contoh:

```bm
nama = "Ayu"
nilai = [80, 90, 100]

pastikan_benar(panjang(nama) > 0)
pastikan_sama(panjang(nilai), 3)
pastikan_tidak_sama(nama, "")
pastikan_salah(berisi(nilai, 10))
```

## Test Modul Lokal

Misalnya ada modul:

```text
src/domain/produk.bm
```

Test-nya:

```bm
pakai "../src/domain/produk.bm" sebagai produk

item = produk.buat("BK-01", "Buku", "ATK", 12000, 10, 3)

pastikan_sama(item["kode"], "BK-01")
pastikan_sama(item["harga"], 12000)
cetak "Tes produk lulus"
```

## Workflow Harian

Untuk proyek besar, pakai urutan ini:

```bash
bm format --cek
bm cek --ketat
bm tes
bm bangun --ketat
python build/utama.py
```

Artinya:

- `bm format --cek`: memastikan kode rapi tanpa mengubah file.
- `bm cek --ketat`: memeriksa sintaks dan warning gaya.
- `bm tes`: menjalankan semua test `.bm`.
- `bm bangun --ketat`: membuat output Python setelah lolos cek.

## Tips Menulis Test

- Mulai dari fungsi yang paling sering dipakai.
- Test hasil sukses dan hasil gagal.
- Jangan bergantung pada input manual di test.
- Buat data test kecil, jelas, dan mudah dibaca.
- Pakai pesan custom agar error lebih cepat dipahami.

Contoh pesan custom:

```bm
pastikan_sama(total, 50000, "Total transaksi harus 50000")
```

