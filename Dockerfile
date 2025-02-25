FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libsqlite3-dev \
    libsqlite3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código y datos
COPY . .

# Inicializar base de datos
RUN python -c "from main import init_db; init_db()"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]