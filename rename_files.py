import os
import argparse

def rename_files_sequentially(directory_path):
    """
    Renames files in the given directory to sequential numbers (1.ext, 2.ext, ...),
    preserving the original file extensions.
    """
    print(f"Memproses direktori: {directory_path}")
    if not os.path.isdir(directory_path):
        print(f"Error: Direktori tidak ditemukan: {directory_path}")
        return

    try:
        # Ambil daftar file saja, dan urutkan untuk konsistensi
        filenames = sorted([f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))])
    except OSError as e:
        print(f"Error saat membaca daftar file di {directory_path}: {e}")
        return

    if not filenames:
        print(f"Tidak ada file yang ditemukan di {directory_path}.")
        return

    count = 1
    renamed_count = 0
    for filename in filenames:
        try:
            name, ext = os.path.splitext(filename)
            new_filename = f"{count}{ext}"
            old_filepath = os.path.join(directory_path, filename)
            new_filepath = os.path.join(directory_path, new_filename)

            # Hindari menimpa file yang sudah ada dengan nama baru, kecuali itu file yang sama
            # (misalnya, jika hanya case yang berbeda, yang tidak relevan di beberapa FS)
            if os.path.exists(new_filepath):
                if old_filepath.lower() == new_filepath.lower() and old_filepath != new_filepath :
                    # Kasus di mana nama file hanya berbeda dalam case, dan sistem file case-sensitive
                    # Izinkan penggantian nama dalam kasus ini.
                    pass
                elif old_filepath == new_filepath:
                    # File sudah memiliki nama yang diinginkan, tidak perlu diubah
                    print(f"File {filename} sudah memiliki nama target {new_filename}. Dilewati.")
                    count += 1
                    continue
                else:
                    print(f"Peringatan: Nama file baru {new_filename} sudah ada di {directory_path}. File {filename} dilewati.")
                    # Pertimbangkan untuk tidak menaikkan count di sini jika ingin mencoba angka berikutnya,
                    # atau biarkan untuk menjaga urutan yang ketat dari file yang diproses.
                    # Untuk saat ini, kita lewati file ini dan lanjutkan dengan file berikutnya dan nomor berikutnya.
                    # Jika ingin nomor tetap berurutan untuk file yang berhasil di-rename, count harus dinaikkan
                    # hanya jika rename berhasil. Namun, ini bisa menyebabkan gap jika banyak file dilewati.
                    # Alternatifnya, jika file target ada, coba nomor berikutnya untuk file saat ini.
                    # Untuk kesederhanaan, kita lewati dan lanjutkan.
                    continue


            os.rename(old_filepath, new_filepath)
            print(f"Berhasil diubah: {old_filepath} -> {new_filepath}")
            renamed_count += 1
            count += 1
        except OSError as e:
            print(f"Error saat mengubah nama file {filename} di {directory_path}: {e}")
        except Exception as e:
            print(f"Terjadi kesalahan tak terduga dengan file {filename}: {e}")

    print(f"Selesai memproses {directory_path}. Berhasil mengubah nama {renamed_count} file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mengubah nama file di subdirektori A dan B menjadi nomor urut.")
    parser.add_argument(
        "--base_dirs",
        nargs='+',
        default=[
            "/TESIS/CDSR-CycleGAN/data/arsip/test",
            "/TESIS/CDSR-CycleGAN/data/arsip/train",
            "/TESIS/CDSR-CycleGAN/data/S-color0.5/test",
            "/TESIS/CDSR-CycleGAN/data/S-color0.5/train",
        ],
        help="Daftar direktori dasar yang berisi subfolder A dan B untuk diproses."
    )
    parser.add_argument(
        "--subdirs_to_process",
        nargs='+',
        default=["A", "B"],
        help="Nama subdirektori (misalnya, A, B) yang akan diproses di setiap base_dir."
    )

    args = parser.parse_args()

    target_parent_dirs = args.base_dirs
    subdirs_to_rename = args.subdirs_to_process

    print("Memulai skrip penggantian nama file...")
    for parent_dir in target_parent_dirs:
        for subdir_name in subdirs_to_rename:
            current_target_dir = os.path.join(parent_dir, subdir_name)
            rename_files_sequentially(current_target_dir)
            print("-" * 40)

    print("Skrip selesai.")
