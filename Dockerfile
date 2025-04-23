FROM python:3.10-slim

# Install system dependencies for Tesseract and poppler (for pdf2image), and libgl (if required)
RUN apt-get update && \
    apt-get install -y \
        tesseract-ocr \
        libtesseract-dev \
        poppler-utils \
        libgl1-mesa-glx \
        gcc \
        g++ \
        build-essential \
        wget \
        && rm -rf /var/lib/apt/lists/*

# Optional: Install language packs for Tesseract if you need to support other languages
# RUN apt-get install -y tesseract-ocr-eng tesseract-ocr-script-latn

# Set workdir
WORKDIR /app

# Copy requirements
COPY requirements.txt /app/requirements.txt

# Install Python dependencies (add your OCR, PDF, FastAPI, Uvicorn, pandas etc. here)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Expose port
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
