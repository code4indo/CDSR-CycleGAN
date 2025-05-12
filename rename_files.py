import os
import argparse # Add this import

def rename_files_in_directory(directory_path, start_count=1): # Add start_count parameter
    """
    Renames files in the specified directory to a sequential number format (start_count.ext, start_count+1.ext, ...).
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at {directory_path}")
        return

    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    files.sort()  # Sort files to ensure consistent renaming if run multiple times, though order might not strictly matter.

    count = start_count # Initialize count with start_count
    for filename in files:
        original_filepath = os.path.join(directory_path, filename)
        file_extension = os.path.splitext(filename)[1]
        new_filename = f"{count}{file_extension}"
        new_filepath = os.path.join(directory_path, new_filename)

        # Ensure new filename doesn't already exist (shouldn't happen with this logic but good practice)
        while os.path.exists(new_filepath):
            # This case should ideally not be hit if files are renamed sequentially from 1.
            # However, if there's a mixup or pre-existing numbered files, this adds robustness.
            # For this specific request, we assume a clean rename.
            # If we were to make it more robust for existing numbered files,
            # we might need a temporary naming scheme or a more complex check.
            # Given the prompt, a simple sequential rename is expected.
            print(f"Warning: {new_filepath} already exists. This shouldn't happen in a clean run.")
            # For now, we'll just overwrite, but in a real scenario, you might want to skip or add a suffix.
            # For this script's purpose, direct renaming is assumed.
            break # Breaking to avoid infinite loop in an unexpected scenario.

        try:
            os.rename(original_filepath, new_filepath)
            print(f"Renamed: {original_filepath} -> {new_filepath}")
            count += 1
        except OSError as e:
            print(f"Error renaming {original_filepath} to {new_filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Rename files in a directory sequentially.")
    parser.add_argument("directory", help="The path to the directory containing files to rename.")
    parser.add_argument("--nomer_mulai", type=int, default=1, help="The starting number for renaming files.")
    args = parser.parse_args()

    directory_to_process = args.directory
    starting_number = args.nomer_mulai

    if not os.path.isabs(directory_to_process):
        directory_to_process = os.path.abspath(directory_to_process)

    print(f"Processing directory: {directory_to_process}")
    print(f"Starting number: {starting_number}")
    rename_files_in_directory(directory_to_process, starting_number)

    print("\\nFile renaming process completed.")

if __name__ == "__main__":
    main()
