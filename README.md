# Panduan Mencoba CDSR-CycleGAN

## Pendahuluan

CDSR-CycleGAN adalah implementasi yang ditingkatkan dari arsitektur CycleGAN untuk translasi gambar antar domain tanpa pasangan (unpaired image-to-image translation). Metode ini menambahkan beberapa mekanisme perhatian (attention) dan jaringan encoder tambahan untuk meningkatkan kualitas hasil translasi gambar.

## Persiapan Lingkungan

### Clone Repository

```bash
git clone https://github.com/code4indo/CDSR-CycleGAN.git
cd CDSR-CycleGAN
```

### Persyaratan Sistem

*   Python 3.6+
*   CUDA-capable GPU (direkomendasikan)

### Instalasi Dependensi (Menggunakan Poetry)

Pastikan Anda telah menginstal [Poetry](https://python-poetry.org/docs/#installation).

Repositori ini sudah menyertakan file `pyproject.toml` yang mendefinisikan dependensi proyek. Untuk menginstal dependensi ini menggunakan Poetry, jalankan perintah berikut di direktori root repositori:

```bash
poetry install
```

Perintah ini akan membuat lingkungan virtual (jika belum ada) dan menginstal semua paket yang diperlukan sesuai dengan file `pyproject.toml` dan `poetry.lock`.

Untuk mengaktifkan lingkungan virtual yang dikelola oleh Poetry    
cara 1:   
poetry env activate dan poetry akan menunjukan virtual env terkait dan lanjutkan dengan copy paste path tersebut 

cara 2:   
secara manual, Anda bisa menggunakan perintah `source` dengan path ke skrip aktivasi lingkungan virtual. Pertama, dapatkan path ke lingkungan virtual:

```bash
poetry env info --path
```

Salin path yang ditampilkan. Kemudian, aktifkan lingkungan menggunakan perintah `source` diikuti dengan path tersebut dan `/bin/activate`:

```bash
source $(poetry env info --path)/bin/activate
# Contoh jika path yang didapat adalah /home/user/.cache/pypoetry/virtualenvs/my-project-py3.9:
# source /home/user/.cache/pypoetry/virtualenvs/my-project-py3.9/bin/activate
```
Setelah shell aktif, Anda dapat menjalankan perintah Python secara langsung (misalnya, `python train.py ...`).


## Struktur Dataset

Dataset harus disusun dengan struktur berikut (lihat `datasets.py:16-19`):

```
data/
└── S-color0.5/
    ├── train/
    │   ├── A/  # Gambar domain sumber untuk pelatihan
    │   └── B/  # Gambar domain target untuk pelatihan
    └── test/
        ├── A/  # Gambar domain sumber untuk pengujian
        └── B/  # Gambar domain target untuk pengujian
```

Setiap folder harus berisi gambar dengan format yang didukung (`JPG`, `PNG`, dll).

## Proses Pelatihan

### Memulai Server Visdom

Sebelum memulai pelatihan, jalankan server Visdom untuk visualisasi:

```bash
python -m visdom.server
```

Server Visdom akan berjalan di `http://localhost:8097`.

### Parameter Pelatihan

Berikut adalah parameter yang dapat disesuaikan untuk pelatihan (lihat `train.py:30-48`).

### Menjalankan Pelatihan

```bash
python train.py --dataroot data/S-color0.5 --n_epochs 100 --batchSize 1 --size 256
```

Parameter penting yang dapat disesuaikan:

*   `--n_epochs`: Jumlah epoch pelatihan (default: 100)
*   `--batchSize`: Ukuran batch (default: 1)
*   `--lr`: Learning rate (default: 0.0001)
*   `--dataroot`: Direktori root dataset (default: `data/S-color0.5`)
*   `--size`: Ukuran gambar (default: 256)
*   `--cuda`: Gunakan GPU untuk komputasi (default: true)

### Penyimpanan Model

Selama pelatihan, model akan disimpan secara otomatis di direktori `output` (lihat `train.py:272-277`).

## Proses Pengujian

Setelah pelatihan selesai, Anda dapat menguji model dengan perintah:

```bash
python test.py --dataroot data/S-color0.5 --cuda
```

### Parameter Pengujian

Berikut adalah parameter yang dapat disesuaikan untuk pengujian:

*   `--batchSize`: Ukuran batch (default: 1)
*   `--dataroot`: Direktori root dataset (default: `data/S-color0.5`)
*   `--size`: Ukuran gambar (default: 256)
*   `--cuda`: Gunakan GPU untuk komputasi (default: true)
*   `--generator_A2B`: Path ke file checkpoint generator A2B (default: `Output/S-color0.5/model/netG_A2B.pth`)
*   `--generator_B2A`: Path ke file checkpoint generator B2A (default: `Output/S-color0.5/model/netG_B2A.pth`)
*   `--generator_E1`: Path ke file checkpoint encoder E1 (default: `Output/S-color0.5/model/netG_E1.pth`)
*   `--generator_E2`: Path ke file checkpoint encoder E2 (default: `Output/S-color0.5/model/netG_E2.pth`)

### Hasil Pengujian

Hasil pengujian akan disimpan di direktori `output` (lihat `test.py:88-89`).

Gambar hasil transformasi akan disimpan dengan format berikut (lihat `test.py:100-102`).

### Visualisasi Hasil

Hasil transformasi gambar dapat dilihat di direktori:

*   `Output/S-color0.5/result/img_a11/`: Hasil transformasi dari domain B ke A
*   `Output/S-color0.5/result/img_b11/`: Hasil transformasi dari domain A ke B

Informasi waktu pemrosesan juga akan dicatat (lihat `test.py:109-117`).

## Arsitektur Model

CDSR-CycleGAN menggunakan beberapa komponen utama:

*   **Generator AtoB**: Mentransformasi gambar dari domain A ke domain B
*   **Generator BtoA**: Mentransformasi gambar dari domain B ke domain A
*   **Encoder S1 dan S2**: Jaringan encoder tambahan untuk meningkatkan kualitas transformasi
*   **Discriminator A dan B**: Membedakan gambar asli dan palsu

## Tips dan Troubleshooting

*   **Penggunaan GPU**:
    *   Pastikan CUDA diinstal dengan benar.
    *   Anda dapat mengatur GPU yang digunakan dengan parameter `CUDA_VISIBLE_DEVICES`:
        ```bash
        export CUDA_VISIBLE_DEVICES=0  # Gunakan GPU pertama
        ```
*   **Masalah Memori**:
    *   Jika mengalami masalah memori GPU, coba kurangi ukuran batch atau ukuran gambar.
    *   Gunakan parameter `--size` dengan nilai yang lebih kecil.
*   **Kualitas Hasil**:
    *   Kualitas hasil sangat bergantung pada dataset yang digunakan.
    *   Pastikan gambar dalam dataset memiliki kualitas yang baik dan konsisten.
*   **Waktu Pelatihan**:
    *   Pelatihan dapat memakan waktu lama tergantung pada jumlah epoch dan ukuran dataset.
    *   Gunakan parameter `--n_epochs` yang lebih kecil untuk pengujian awal.
*   **Visualisasi dengan Visdom**:
    *   Pastikan server Visdom berjalan sebelum memulai pelatihan.
    *   Akses visualisasi di browser melalui `http://localhost:8097`.

## Referensi

*   **Kode sumber**: [code4indo/CDSR-CycleGAN](https://github.com/code4indo/CDSR-CycleGAN)
*   **Arsitektur model**: Lihat file `models.py` untuk detail implementasi.
*   **Proses pelatihan**: Lihat file `train.py` untuk detail alur pelatihan.
*   **Proses pengujian**: Lihat file `test.py` untuk detail alur pengujian.

Dengan mengikuti panduan ini, Anda dapat mencoba metode CDSR-CycleGAN untuk translasi gambar antar domain.

---

**Notes:**

*   Panduan ini dibuat berdasarkan analisis kode dari repositori `code4indo/CDSR-CycleGAN`.
*   Struktur dataset dan parameter yang digunakan mengacu pada nilai default dalam kode.
*   Beberapa parameter mungkin perlu disesuaikan berdasarkan kebutuhan dan spesifikasi hardware Anda.

---

**Wiki pages you might want to explore:**

*   [Overview (code4indo/CDSR-CycleGAN)](https://github.com/code4indo/CDSR-CycleGAN/wiki)
