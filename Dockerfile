FROM python:3.11-slim

# poppler-utils は pdf2image に必要
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV PORT=8080
CMD ["functions-framework", "--target=season_ocr_http", "--port=8080"]
