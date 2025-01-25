import os
import shutil
from datetime import datetime
from PIL import Image, ExifTags

# Directories
INPUT_DIR = "/share/CACHEDEV2_DATA/Bilder_Videos/ImageSorterInput"
OUTPUT_DIR = "/share/CACHEDEV2_DATA/Bilder_Videos/ImageSorterOutput"
ERROR_DIR = os.path.join(INPUT_DIR, "Error")

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def extract_creation_date(file_path):
    try:
        with Image.open(file_path) as img:
            exif = img._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if tag == "DateTimeOriginal":
                        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").strftime("%Y_%m_%d")
    except Exception as e:
        print("Error extracting date from {0}: {1}".format(file_path, str(e)))
    
    # If EXIF data is not available, use file modification time
    return datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y_%m_%d")

def sort_images():
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            file_path = os.path.join(INPUT_DIR, filename)
            creation_date = extract_creation_date(file_path)
            
            # Create year-month folder
            year_month = creation_date[:7]  # YYYY_MM
            output_folder = os.path.join(OUTPUT_DIR, year_month)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            # Move file
            new_file_path = os.path.join(output_folder, "{0}_{1}".format(creation_date, filename))
            shutil.move(file_path, new_file_path)
            print("Moved {0} to {1}".format(filename, new_file_path))

if __name__ == "__main__":
    sort_images()

