# Data Quality Service - CulturalRoute AI

Este servicio es responsable de la ingesta masiva de datos culturales a través de archivos CSV, realizando validaciones estructurales y persistiendo los resultados en una base de datos.

## Requisitos
- Python 3.11+
- Docker y Docker Compose
- PostgreSQL (o cualquier base de datos compatible con SQLAlchemy)

## Instalación de dependencias (para desarrollo local sin Docker)
```bash
pip install fastapi uvicorn python-multipart sqlalchemy psycopg2-binary python-dotenv
```

## Ejecución

### Con Docker Compose (Recomendado para desarrollo y producción)
1.  Asegúrate de tener Docker y Docker Compose instalados.
2.  Navega a la raíz del proyecto (`/home/ubuntu/project/Proyecto-CulturalRoute-AI--main`).
3.  Levanta los servicios (base de datos y microservicio):
    ```bash
    docker-compose up --build
    ```
    Esto construirá la imagen del servicio, creará la base de datos PostgreSQL y levantará ambos contenedores. Las tablas de la base de datos se crearán automáticamente al iniciar el servicio.

### Ejecución local (solo el servicio, requiere PostgreSQL corriendo aparte)
1.  Asegúrate de tener las dependencias instaladas (`pip install ...`).
2.  Configura la variable de entorno `DATABASE_URL` para tu base de datos PostgreSQL local. Ejemplo:
    ```bash
    export DATABASE_URL="postgresql://user:password@localhost:5432/data_quality_db"
    ```
3.  Navega a la carpeta del servicio (`services/data-quality-service`).
4.  Ejecuta el servicio:
    ```bash
    python main.py
    ```

## Endpoints

### 1. Cargar CSV
`POST /imports`
- **Request:** Multipart Form con el campo `file`.
- **Response:** 202 Accepted. Retorna el `batch_id` y estado inicial. El procesamiento se realiza en segundo plano y los resultados se persisten en la base de datos.

### 2. Consultar Estado del Lote
`GET /imports/{batch_id}`
- **Response:** 200 OK. Retorna el estado actual del procesamiento, así como el conteo de filas procesadas, válidas e inválidas, obtenidos de la base de datos.

### 3. Consultar Errores
`GET /imports/{batch_id}/errors`
- **Response:** 200 OK. Lista detalladamente los errores encontrados durante la validación, incluyendo el número de fila, el campo afectado y el mensaje de error, persistidos en la base de datos.

## Reglas de Validación
- Las columnas obligatorias son: `nombre`, `ciudad`, `direccion`.
- El parser CSV detecta automáticamente el delimitador (`,` o `;`) y maneja codificaciones `UTF-8` y `Latin-1`.
- Si una fila carece de alguno de los valores requeridos, se marca como inválida y se registra el error en la base de datos.
