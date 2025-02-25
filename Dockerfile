FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libsqlite3-dev \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copiar solo requirements.txt primero para cachear dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Inicializar BBDD (ahora main.py ya está copiado)
RUN python -c "from main import init_db; init_db()"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]