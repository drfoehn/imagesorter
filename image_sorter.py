
import shutil
import os
import subprocess
from datetime import datetime
import logging
from PIL import Image, ExifTags
import platform
from pathlib import Path

# Setup logging
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Directories
INPUT_DIR = Path(os.environ.get('INPUT_DIR', '/app/input'))
OUTPUT_DIR = Path(os.environ.get('OUTPUT_DIR', '/app/output'))
UNSUPPORTED_DIR = INPUT_DIR / "Unsupported_Files"
NO_CREATION_DATE_DIR = INPUT_DIR / "No_CreationDate"
ERROR_FILES_DIR = INPUT_DIR / "Error_Files"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UNSUPPORTED_DIR.mkdir(parents=True, exist_ok=True)
NO_CREATION_DATE_DIR.mkdir(parents=True, exist_ok=True)
ERROR_FILES_DIR.mkdir(parents=True, exist_ok=True)

print("Directories set up.")

# Supported extensions
supported_extensions = {'.jpg', '.jpeg', '.png', '.mov', '.mp4', '.heic'}

def extract_creation_date_image(file_path):
    try:
        img = Image.open(file_path)
        if "exif" in img.info:
            exif_data = img._getexif()
            # Find the creation time in EXIF data
            for tag, value in exif_data.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                if decoded == "DateTimeOriginal":
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").strftime("%Y_%m_%d")
    except Exception as e:
        logging.error(f"Failed to extract creation date from image {file_path}: {e}")
    return None

def extract_creation_date_ffprobe(file_path):
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream_tags=creation_time',
        '-of', 'csv=p=0',
        str(file_path)
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        creation_time = result.stdout.strip()
        if creation_time:
            return datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y_%m_%d")
    except Exception as e:
        logging.error(f"Failed to extract creation date from {file_path} with ffprobe: {e}")
    return None

def extract_creation_date(file_path):
    if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.heic'}:
        return extract_creation_date_image(file_path)
    elif file_path.suffix.lower() in {'.mov', '.mp4'}:
        return extract_creation_date_ffprobe(file_path)
    
    # Fallback to file system date
    if platform.system() == 'Windows':
        timestamp = file_path.stat().st_ctime
    else:
        stat = file_path.stat()
        try:
            timestamp = stat.st_birthtime
        except AttributeError:
            timestamp = stat.st_mtime
    return datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d')

def move_file(src_path, dest_dir, original_name):
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / original_name
    if not dest_path.exists():
        shutil.move(str(src_path), str(dest_path))
        logging.info(f"Moved file: {original_name} to {dest_dir}")
        print(f"Moved file: {original_name} to {dest_dir}")
    else:
        logging.warning(f"File already exists in destination: {original_name}")
        print(f"File already exists in destination: {original_name}")

def main():
    for file_path in INPUT_DIR.iterdir():
        if file_path.is_file():
            if file_path.name.startswith('.'):
                continue  # Skip hidden files
            if file_path.suffix.lower() not in supported_extensions:
                move_file(file_path, UNSUPPORTED_DIR, file_path.name)
                continue
            
            creation_date = extract_creation_date(file_path)
            if not creation_date:
                move_file(file_path, NO_CREATION_DATE_DIR, file_path.name)
                continue
            
            new_filename = f"{creation_date}_{file_path.name}"
            output_subdir = OUTPUT_DIR / creation_date[:7]
            try:
                move_file(file_path, output_subdir, new_filename)
            except Exception as e:
                logging.error(f"Error handling file {file_path.name}: {e}")
                shutil.move(str(file_path), str(ERROR_FILES_DIR))

if __name__ == "__main__":
    main()
    logging.info("Script finished running.")

