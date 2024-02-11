# Images Sorter

This script may be used as standalone or as Docker image on a QNAP system (ContainerStation)

### What it does:
It scrolls through the specified INPUT_DIR and:
1) Extracts EXIF-Info from the image - Date of creation
3) Renames the file with the date of creation (YYYY_MM_dd) following the original file name
4) Creates a new folder in the specified OUTPUT_DIR for the month the image was created in case it does not already exist
5) Moves the file into that folder in case it does not already exist there.
6) Saves a log-file 

_Note: Subdirectories are included in the iterations_

### It can handle the following files:
 - Imagesfiles
   - JPG
   - PNG
   - HEIC
 - Videofiles
   - MOV
   - MP4

you can extend the list by adding the extension to the `supported_extensions` variable


### Prerequisits:

#### Necessary libraries:
- Pillow

To run it locally you need to install `ffmpeg` on your machine

##### For Windows
On Windows, installing these tools involves downloading executable installers or binary packages.

FFmpeg:

- Download the latest FFmpeg build from the official website: https://ffmpeg.org/download.html
- Extract the downloaded archive. 
- Add the path to the bin directory within the extracted folder to your system's PATH environment variable.

##### For Linux run
- `sudo apt-get update`
- `sudo apt-get install ffmpeg`

##### For Mac (_using Homebrew_) run:
- `brew install ffmpeg`




### Dockerinstallation
For Docker please use the .tar image file to import to the designated server or QNAP system

### Disclaimer of Liability
The author of this code ("the author") hereby disclaims any and all liability 
for any damage, loss, or liability to you or any third party, 
whether direct, indirect, special, incidental, consequential, or punitive, 
arising from the use, misuse, or inability to use this code. 

The code is provided "as is" without warranty of any kind, 
either expressed or implied, including but not limited to the warranties 
of merchantability, fitness for a particular purpose, or non-infringement. 

The user assumes all responsibility and risk for the use of this code. 
The author does not guarantee the accuracy, reliability, completeness, 
or timeliness of the content contained in this code and may make changes 
to it at any time without notice. 

Users are cautioned to ensure that the code is suitable for their purposes before using it.


### License: ShareAlike