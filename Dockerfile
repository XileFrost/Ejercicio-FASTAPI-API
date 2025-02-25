FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y \
    gcc \
    python3-dev \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -c "from main import init_db; init_db()"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]