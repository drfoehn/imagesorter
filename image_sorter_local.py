import shutil
import os
import subprocess
from datetime import datetime
import logging
from PIL import Image, ExifTags
import platform

# Setup logging
log_dir = "/share/CACHEDEV1_DATA/Container/ImageSorter/"
log_file = os.path.join(log_dir, "image_sorter_log.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Directories
INPUT_DIR = "/share/CACHEDEV2_DATA/Bilder_Videos/ImageSorterInput"
OUTPUT_DIR = "/share/CACHEDEV2_DATA/Bilder_Videos/ImageSorterOutput"
UNSUPPORTED_DIR = os.path.join(INPUT_DIR, "Unsupported_Files")
NO_CREATION_DATE_DIR = os.path.join(INPUT_DIR, "No_CreationDate")
ERROR_FILES_DIR = os.path.join(INPUT_DIR, "Error_Files")

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UNSUPPORTED_DIR, exist_ok=True)
os.makedirs(NO_CREATION_DATE_DIR, exist_ok=True)
os.makedirs(ERROR_FILES_DIR, exist_ok=True)

print("Directories set up.")

# Supported extensions
supported_extensions = {'.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.mov', '.MOV', '.mp4', '.MP4', '.heic', '.HEIC'}

def extract_creation_date_image(file_path):
    try:
        with Image.open(file_path) as img:
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
        file_path
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
    # First, try to extract date from EXIF data for images
    if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
        date = extract_creation_date_image(file_path)
        if date:
            return date
    
    # If it's a video file or EXIF extraction failed, try ffprobe
    if file_path.lower().endswith(('.mov', '.mp4')):
        date = extract_creation_date_ffprobe(file_path)
        if date:
            return date
    
    # If all else fails, use file system date
    stat = os.stat(file_path)
    try:
        timestamp = stat.st_birthtime
    except AttributeError:
        # We're probably on Linux. No easy way to get creation dates here,
        # so we'll settle for when its content was last modified.
        timestamp = stat.st_mtime  # Fallback to the modification time

    # Convert the timestamp to datetime and format it
    date = datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d')
    return date

def move_file(src_path, dest_dir, original_name):
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, original_name)
    if not os.path.exists(dest_path):
        shutil.move(src_path, dest_path)
        logging.info(f"Moved file: {original_name} to {dest_dir}")
        print(f"Moved file: {original_name} to {dest_dir}")
    else:
        logging.warning(f"File already exists in destination: {original_name}")
        print(f"File already exists in destination: {original_name}")

def main():
    for root, dirs, files in os.walk(INPUT_DIR, topdown=True):
        if root != INPUT_DIR:
            break  # Skip processing any subdirectories

        for filename in files:
            full_path = os.path.join(root, filename)
            if filename.startswith('.'):
                continue  # Skip hidden files

            if not any(filename.lower().endswith(ext) for ext in supported_extensions):
                move_file(full_path, UNSUPPORTED_DIR, filename)
                continue

            creation_date = extract_creation_date(full_path)
            if not creation_date:
                move_file(full_path, NO_CREATION_DATE_DIR, filename)
                continue

            new_filename = f"{creation_date}_{filename}"
            output_subdir = os.path.join(OUTPUT_DIR, creation_date[:7])

            try:
                move_file(full_path, output_subdir, new_filename)
            except Exception as e:
                logging.error(f"Error handling file {filename}: {e}")
                shutil.move(full_path, ERROR_FILES_DIR)

    logging.info("Script finished running.")

if __name__ == "__main__":
    main()

