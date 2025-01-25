# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variables
ENV INPUT_DIR=/app/input
ENV OUTPUT_DIR=/app/output
# Define environment variable
#ENV NAME World

# Create volumes for input and output
VOLUME ["/app/input", "/app/output"]

# Run image_sorter.py when the container launches
CMD ["python", "./image_sorter.py"]

#docker run -e INPUT_DIR=/path/to/input -e OUTPUT_DIR=/path/to/output -v /host/input/path:/path/to/input -v /host/output/path:/path/to/output image_sorter
#docker run -v /host/input/path:/app/input -v /host/output/path:/app/output image_sorter