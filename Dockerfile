# syntax=docker/dockerfile:1.6

# Usamos Python 3.10 para compatibilidad con numpy~=1.22.4 (en requirements.txt)
FROM python:3.10-slim

# Evita que Python escriba .pyc y fuerza logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias mínimas del sistema (por si alguna librería requiere compilación)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala primero para mejor cache
COPY requirements.txt requirements.txt

# Asegura toolchain de build para sdists (setuptools.build_meta, wheels, etc.)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Instala dependencias de runtime
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir xgboost
# Copia el código del repo
COPY . .

# Cloud Run usa PORT (normalmente 8080)
ENV PORT=8080

# Levanta FastAPI con uvicorn escuchando en 0.0.0.0:$PORT
CMD ["sh", "-c", "uvicorn challenge.api:app --host 0.0.0.0 --port ${PORT}"]