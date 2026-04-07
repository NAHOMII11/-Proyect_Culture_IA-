FROM python:3.11

WORKDIR /app

# Instalamos las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código de la API
COPY . .

# Exponemos el puerto 8000 y arrancamos uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]