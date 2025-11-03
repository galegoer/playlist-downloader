FROM python:3.12-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y \
        ffmpeg && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy code and requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Command to run your script
ENTRYPOINT ["python", "src/main.py"]