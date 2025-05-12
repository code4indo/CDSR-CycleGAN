# Panduan Mencoba CDSR-CycleGAN (Indonesian Guide)

## Pendahuluan

CDSR-CycleGAN adalah implementasi yang ditingkatkan dari arsitektur CycleGAN untuk translasi gambar antar domain tanpa pasangan (unpaired image-to-image translation). Metode ini menambahkan beberapa mekanisme perhatian (attention) dan jaringan encoder tambahan untuk meningkatkan kualitas hasil translasi gambar.

## Persiapan Lingkungan

### 1. Clone Repository

```bash
git clone https://github.com/code4indo/CDSR-CycleGAN.git
cd CDSR-CycleGAN
```

### 2. Persyaratan Sistem

*   Python 3.6+
*   CUDA-capable GPU (direkomendasikan)
*   [Poetry](https://python-poetry.org/docs/#installation) (untuk manajemen dependensi)

### 3. Instalasi Dependensi (Menggunakan Poetry)

Repositori ini menggunakan Poetry untuk mengelola dependensi (lihat `pyproject.toml`).

```bash
poetry install
```

Perintah ini akan membuat lingkungan virtual dan menginstal semua paket yang diperlukan.

### 4. Aktifkan Lingkungan Virtual Poetry

Pilih salah satu cara berikut:

*   **Cara 1 (Otomatis):**
    ```bash
    poetry shell
    ```
    Ini akan mengaktifkan lingkungan virtual dalam shell baru.

*   **Cara 2 (Manual):**
    a. Dapatkan path lingkungan virtual:
    ```bash
    poetry env info --path
    ```
    b. Aktifkan menggunakan path tersebut:
    ```bash
    # Ganti <path-ke-env> dengan output dari perintah sebelumnya
    source <path-ke-env>/bin/activate
    # Contoh: source /home/user/.cache/pypoetry/virtualenvs/my-project-py3.9/bin/activate
    ```

Setelah lingkungan aktif, Anda dapat menjalankan skrip Python (misalnya, `python train.py ...`).

## Struktur Dataset

Susun dataset Anda seperti berikut:

```
data/
└── NAMA_DATASET_ANDA/  # Ganti dengan nama dataset Anda (misal: S-color0.5)
    ├── train/
    │   ├── A/  # Gambar domain sumber (pelatihan)
    │   └── B/  # Gambar domain target (pelatihan)
    └── test/
        ├── A/  # Gambar domain sumber (pengujian)
        └── B/  # Gambar domain target (pengujian)
```

Gunakan format gambar yang didukung (JPG, PNG, dll.). Ganti `S-color0.5` dalam contoh perintah di bawah dengan `NAMA_DATASET_ANDA`.

## Proses Pelatihan

### 1. Mulai Server Visdom (Opsional, untuk Visualisasi)

```bash
python -m visdom.server
```

Akses visualisasi di `http://localhost:8097`.

### 2. Jalankan Pelatihan

```bash
python train.py --dataroot data/NAMA_DATASET_ANDA --n_epochs 100 --batchSize 1 --size 256 --cuda
```

Parameter penting:

*   `--dataroot`: Direktori root dataset (wajib diubah).
*   `--n_epochs`: Jumlah epoch pelatihan (default: 100).
*   `--decay_epoch`: Epoch untuk mulai mengurangi learning rate (default: 50).
*   `--batchSize`: Ukuran batch (default: 1). Sesuaikan berdasarkan memori GPU.
*   `--lr`: Learning rate awal (default: 0.0001).
*   `--size`: Ukuran gambar input (default: 256).
*   `--cuda`: Gunakan GPU (default: true). Set ke `false` jika tidak ada GPU.

Model checkpoint akan disimpan secara otomatis di `Output/NAMA_DATASET_ANDA/model/`.

## Proses Pengujian

### 1. Jalankan Pengujian

Pastikan model hasil pelatihan ada di direktori `Output/NAMA_DATASET_ANDA/model/`.

```bash
python test.py --dataroot data/NAMA_DATASET_ANDA --cuda
```

Parameter penting:

*   `--dataroot`: Direktori root dataset (wajib diubah).
*   `--size`: Ukuran gambar input (default: 256).
*   `--cuda`: Gunakan GPU (default: true).
*   `--generator_A2B`, `--generator_B2A`, `--generator_E1`, `--generator_E2`: Path ke file checkpoint model (default menggunakan path di `Output/NAMA_DATASET_ANDA/model/`).

### 2. Hasil Pengujian

Hasil gambar transformasi akan disimpan di:

*   `Output/NAMA_DATASET_ANDA/result/img_a11/` (Hasil B -> A)
*   `Output/NAMA_DATASET_ANDA/result/img_b11/` (Hasil A -> B)

Informasi waktu pemrosesan disimpan di `Output/NAMA_DATASET_ANDA/runtime.txt`.

## Proses Inferensi (Pembersihan Dokumen)

Skrip `inference.py` digunakan untuk melakukan pembersihan pada kumpulan gambar dokumen yang rusak. Skrip ini akan memproses setiap gambar dalam direktori input, memotongnya menjadi bagian-bagian kecil (patch), membersihkan setiap patch menggunakan model generator yang telah dilatih (`netG_A2B.pth`), dan kemudian menggabungkan kembali patch-patch tersebut menjadi gambar utuh yang bersih.

### 1. Jalankan Inferensi

Pastikan Anda memiliki model `netG_A2B.pth` yang telah dilatih (biasanya disimpan di `Output/NAMA_DATASET_ANDA/model/netG_A2B.pth` setelah proses pelatihan, atau Anda bisa menggunakan path kustom).

```bash
python inference.py --input_dir /path/ke/direktori_gambar_rusak/ --cuda
```

Ganti `/path/ke/direktori_gambar_rusak/` dengan path aktual ke direktori yang berisi gambar-gambar dokumen yang ingin Anda bersihkan.

### 2. Parameter Penting

*   `--input_dir` (wajib): Direktori yang berisi gambar-gambar dokumen rusak yang akan diproses.
*   `--output_subdir_name`: Nama subdirektori yang akan dibuat di dalam `--input_dir` untuk menyimpan hasil gambar yang sudah bersih. Default: `cleaned_output`.
*   `--model_path`: Path ke file checkpoint model generator `netG_A2B.pth`. Default: `Output/S-color0.5/model/netG_A2B.pth`. Sesuaikan jika nama dataset atau lokasi model Anda berbeda.
*   `--patch_size`: Ukuran patch yang digunakan untuk memproses gambar (misalnya, 256 untuk 256x256 piksel). Default: `256`. Sebaiknya sama dengan ukuran yang digunakan saat pelatihan.
*   `--input_nc`: Jumlah channel gambar input untuk model. Default: `3`.
*   `--output_nc`: Jumlah channel gambar output untuk model. Default: `3`.
*   `--cuda`: Gunakan GPU untuk komputasi jika tersedia.

### 3. Hasil Inferensi

Hasil gambar yang telah dibersihkan akan disimpan di subdirektori yang ditentukan oleh `--output_subdir_name` (default: `cleaned_output`) di dalam direktori yang Anda berikan pada `--input_dir`. Nama file output akan sama dengan nama file input dengan tambahan `_cleaned.png`.

Contoh: Jika input adalah `/path/ke/direktori_gambar_rusak/dokumen1.jpg`, maka outputnya akan menjadi `/path/ke/direktori_gambar_rusak/cleaned_output/dokumen1_cleaned.png`.

## Arsitektur Model

*   **Generator (AtoB & BtoA)**: Melakukan translasi antar domain.
*   **Encoder (E1 & E2)**: Encoder tambahan untuk fitur.
*   **Discriminator (A & B)**: Membedakan gambar asli dan hasil translasi.

## Tips dan Troubleshooting

*   **GPU**: Pastikan driver CUDA dan PyTorch versi GPU terinstal. Atur GPU spesifik dengan `export CUDA_VISIBLE_DEVICES=0` (gunakan GPU ID 0).
*   **Memori**: Jika kehabisan memori GPU, kurangi `--batchSize` atau `--size`.
*   **Kualitas**: Hasil bergantung pada kualitas dan kuantitas dataset.
*   **Waktu**: Pelatihan bisa lama. Coba dengan `--n_epochs` lebih kecil untuk tes awal.

## Referensi

*   **Kode Sumber**: [code4indo/CDSR-CycleGAN](https://github.com/code4indo/CDSR-CycleGAN)
*   **Detail Implementasi**: Lihat file `models.py`, `train.py`, `test.py`.

---
