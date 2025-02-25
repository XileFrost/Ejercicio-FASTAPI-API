FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libsqlite3-dev \  # Clave para SQLite
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -c "from main import init_db; init_db()"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]