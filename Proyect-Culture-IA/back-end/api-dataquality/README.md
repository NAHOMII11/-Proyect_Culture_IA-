# Data Quality API

API en FastAPI para cargar archivos CSV, validar su contenido y guardar el resultado de la validación en PostgreSQL.

## Funcionalidad

Esta API permite:

- Subir un archivo CSV.
- Crear un batch de importación.
- Validar en segundo plano que el archivo tenga las columnas requeridas.
- Consultar el estado del batch.
- Consultar los errores encontrados por fila y por campo.

---

## Requisitos

- Python 3.11+
- PostgreSQL
- Docker y Docker Compose, si vas a levantar todo en contenedores

---

## Estructura esperada del CSV

El archivo CSV debe contener estas columnas obligatorias:

- `nombre`
- `ciudad`
- `direccion`

### Ejemplo válido

```csv
nombre,ciudad,direccion
Juan,Bogotá,Calle 1
Ana,Medellín,Carrera 10
Pedro,Cali,Avenida 3
```

### Ejemplo con errores

```csv
nombre,ciudad,direccion
Juan,Bogotá,Calle 1
Ana,,Carrera 10
Pedro,Medellín,
```

---

## Endpoints

### 1. `POST /imports`

Recibe un archivo CSV, crea un batch y dispara la validación en background.

### Tipo de entrada

Este endpoint recibe el archivo como `multipart/form-data`.

### Campo requerido

- `file`: archivo con extensión `.csv`

### Ejemplo con `curl`

```bash
curl -X POST "http://localhost:8000/imports" \
  -H "accept: application/json" \
  -F "file=@datos.csv"
```

### Respuesta exitosa

**Código:** `202 Accepted`

```json
{
  "batch_id": "4a7c1f4f-7b64-4c2f-a24e-b0d7d5c0c999",
  "status": "processing",
  "processed_rows": 0,
  "valid_rows": 0,
  "invalid_rows": 0
}
```

### Errores posibles

**400 Bad Request**

Si el archivo no termina en `.csv`:

```json
{
  "detail": "El archivo debe ser un CSV"
}
```

---

### 2. `GET /imports/{batch_id}`

Devuelve el estado del batch y sus contadores.

### Parámetro de ruta

- `batch_id`: identificador del lote generado al subir el CSV

### Ejemplo con `curl`

```bash
curl "http://localhost:8000/imports/4a7c1f4f-7b64-4c2f-a24e-b0d7d5c0c999"
```

### Respuesta exitosa

**Código:** `200 OK`

```json
{
  "batch_id": "4a7c1f4f-7b64-4c2f-a24e-b0d7d5c0c999",
  "status": "completed",
  "processed_rows": 3,
  "valid_rows": 1,
  "invalid_rows": 2
}
```

### Estados posibles

- `processing`: la validación aún está en ejecución.
- `completed`: la validación terminó correctamente.
- `failed`: faltan columnas requeridas o ocurrió un problema de validación.

### Errores posibles

**404 Not Found**

Si el batch no existe:

```json
{
  "detail": "Batch no encontrado"
}
```

---

### 3. `GET /imports/{batch_id}/errors`

Devuelve la lista de errores de validación asociados al batch.

### Parámetro de ruta

- `batch_id`: identificador del lote

### Ejemplo con `curl`

```bash
curl "http://localhost:8000/imports/4a7c1f4f-7b64-4c2f-a24e-b0d7d5c0c999/errors"
```

### Respuesta exitosa

**Código:** `200 OK`

```json
[
  {
    "row_number": 3,
    "field_name": "ciudad",
    "error_type": "missing_field",
    "message": "El campo 'ciudad' es obligatorio"
  },
  {
    "row_number": 4,
    "field_name": "direccion",
    "error_type": "missing_field",
    "message": "El campo 'direccion' es obligatorio"
  }
]
```

### Errores posibles

**404 Not Found**

Si el batch no existe:

```json
{
  "detail": "Batch no encontrado"
}
```

---

## Flujo de uso

1. Subes el archivo con `POST /imports`.
2. Recibes un `batch_id`.
3. Consultas el estado con `GET /imports/{batch_id}`.
4. Si hay errores, los ves con `GET /imports/{batch_id}/errors`.

---

## Ejemplo completo

### 1. Subir archivo

```bash
curl -X POST "http://localhost:8000/imports" \
  -H "accept: application/json" \
  -F "file=@datos.csv"
```

### 2. Revisar estado

```bash
curl "http://localhost:8000/imports/4a7c1f4f-7b64-4c2f-a24e-b0d7d5c0c999"
```

### 3. Revisar errores

```bash
curl "http://localhost:8000/imports/4a7c1f4f-7b64-4c2f-a24e-b0d7d5c0c999/errors"
```

---

## Notas técnicas

- El procesamiento del CSV se ejecuta en background.
- La validación busca columnas obligatorias en minúsculas.
- Si una fila tiene un campo vacío, esa fila se marca como inválida.
- Los resultados se almacenan en PostgreSQL.
- El batch se crea antes de terminar la validación, por eso el POST responde de inmediato con estado `processing`.

---

## Documentación automática

Cuando la API esté levantada, puedes probarla desde Swagger:

- `http://localhost:8000/docs`

---

## Ejemplo de respuesta de error general

```json
{
  "detail": "El archivo debe ser un CSV"
}
```

## Ejemplo de batch no encontrado

```json
{
  "detail": "Batch no encontrado"
}
```