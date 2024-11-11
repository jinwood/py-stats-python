

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for psutil
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python packages with specific versions
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]

