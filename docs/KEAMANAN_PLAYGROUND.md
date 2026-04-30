# Keamanan Playground

Playground Bahasa Manis harus aman secara default, terutama jika dibuka untuk publik.

## Mode Aman Default

`server.py` menjalankan interpreter dengan mode aman:

```python
Interpreter(aman=True)
```

Di mode ini:

- `paket` dimatikan.
- `pakai` dimatikan.
- helper berkas seperti `tulis_berkas` dan `hapus_berkas` dimatikan.
- fitur dasar seperti `cetak`, `jika`, `setiap`, `ulangi`, fungsi, dan helper data tetap aktif.

## Kenapa Perlu Mode Aman

Bahasa Manis punya fitur kuat untuk penggunaan lokal:

- import Python lewat `paket`
- import modul BM lewat `pakai`
- baca dan tulis file lewat helper berkas

Fitur ini berguna untuk belajar dan aplikasi lokal, tetapi berbahaya jika user random bisa menjalankannya di server.

## Menjalankan Playground Lokal

Mode aman:

```bash
python server.py
```

Mode unsafe untuk eksperimen lokal:

```bash
BM_PLAYGROUND_UNSAFE=1 python server.py
```

Jangan gunakan `BM_PLAYGROUND_UNSAFE=1` di server publik.

## Batas Dasar

Playground punya batas ukuran:

- `BM_PLAYGROUND_MAX_CODE_CHARS`
- `BM_PLAYGROUND_MAX_OUTPUT_CHARS`
- `BM_PLAYGROUND_TIMEOUT_SECONDS`

Contoh:

```bash
BM_PLAYGROUND_MAX_CODE_CHARS=10000 BM_PLAYGROUND_MAX_OUTPUT_CHARS=10000 BM_PLAYGROUND_TIMEOUT_SECONDS=5 python server.py
```

Kode pengguna dijalankan di proses worker terpisah. Jika melewati batas waktu, proses worker dihentikan dan playground mengembalikan pesan error.

## Checklist Sebelum Publik

- [ ] Mode unsafe tidak aktif.
- [ ] Server berjalan di environment terisolasi.
- [ ] Reverse proxy membatasi ukuran request.
- [ ] Rate limit aktif jika playground dibuka publik.
- [ ] Log tidak menyimpan data sensitif user.
- [ ] Output dipotong jika terlalu panjang.
- [ ] Timeout eksekusi aktif.
- [ ] Tidak ada token atau rahasia di environment playground.

## Rekomendasi Setelah 1.0

Untuk publik besar, pertimbangkan sandbox yang lebih ketat dari worker proses bawaan:

- batas memori
- working directory sementara
- izin file minimal
- pembersihan file setelah request selesai
