import csv
import io
import re
import unicodedata
import httpx

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.import_batch import ImportBatchDB, ImportErrorDB

REQUIRED_COLUMNS = ["nombre", "ciudad", "direccion"]

def optional_float_field(row: dict, *possible_keys: str):
    for key in possible_keys:
        normalized_key = normalize_text(key)
        value = row.get(normalized_key, "")

        if value is None:
            continue

        value = str(value).strip()
        if value == "":
            continue

        try:
            return float(value.replace(",", "."))
        except ValueError:
            return None

    return None

def normalize_text(value: str) -> str:
    if value is None:
        return ""
    value = str(value).strip()
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


def normalize_cell(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_row_keys(row: dict) -> dict:
    normalized = {}
    for key, value in row.items():
        normalized_key = normalize_text(key)
        normalized[normalized_key] = normalize_cell(value)
    return normalized


def empty_if_missing(row: dict, *possible_keys: str) -> str:
    for key in possible_keys:
        normalized_key = normalize_text(key)
        value = row.get(normalized_key, "")
        if value:
            return value
    return ""


def build_place_payload(row: dict) -> dict:
    return {
        "name": empty_if_missing(row, "nombre", "name"),
        "description": empty_if_missing(row, "descripcion", "description"),
        "category": empty_if_missing(row, "categoria", "category"),
        "address": empty_if_missing(row, "direccion", "address") or None,
        "latitude": optional_float_field(row, "latitude", "latitud"),
        "longitude": optional_float_field(row, "longitude", "longitud"),
        "imagelink": empty_if_missing(row, "imagelink", "image_link", "imagen", "url_imagen") or None,
    }

def send_place_to_api(payload: dict) -> tuple[bool, str]:
    try:
        response = httpx.post(
            settings.places_api_url,
            json=payload,
            timeout=20.0,
        )

        if 200 <= response.status_code < 300:
            return True, ""

        return False, f"Places API respondió {response.status_code}: {response.text}"

    except Exception as e:
        return False, str(e)

def validate_csv(batch_id: str, content: str) -> None:
    db = SessionLocal()
    try:
        batch = db.query(ImportBatchDB).filter(ImportBatchDB.id == batch_id).first()
        if not batch:
            return

        f = io.StringIO(content)

        try:
            sample = content[:1024]
            dialect = csv.Sniffer().sniff(sample, delimiters=",;")
            f.seek(0)
            reader = csv.DictReader(f, dialect=dialect)
        except Exception:
            f.seek(0)
            reader = csv.DictReader(f)

        if reader.fieldnames:
            reader.fieldnames = [normalize_text(name) for name in reader.fieldnames]

        missing_columns = [col for col in REQUIRED_COLUMNS if col not in (reader.fieldnames or [])]
        if missing_columns:
            batch.status = "failed"
            for col in missing_columns:
                db.add(
                    ImportErrorDB(
                        batch_id=batch_id,
                        row_number=1,
                        field_name=col,
                        error_type="missing_column",
                        message=f"Falta la columna requerida '{col}' en el archivo CSV",
                    )
                )
            db.commit()
            return

        processed = 0
        valid = 0
        invalid = 0
        errors_to_save = []

        for i, row in enumerate(reader, start=2):
            processed += 1
            row_errors = []
            row = normalize_row_keys(row)

            for col in REQUIRED_COLUMNS:
                val = row.get(col, "")
                if not val:
                    row_errors.append(
                        ImportErrorDB(
                            batch_id=batch_id,
                            row_number=i,
                            field_name=col,
                            error_type="missing_field",
                            message=f"El campo '{col}' es obligatorio",
                        )
                    )

            if row_errors:
                invalid += 1
                errors_to_save.extend(row_errors)
                continue

            payload = build_place_payload(row)
            ok, error_message = send_place_to_api(payload)

            if ok:
                valid += 1
            else:
                invalid += 1
                errors_to_save.append(
                    ImportErrorDB(
                        batch_id=batch_id,
                        row_number=i,
                        field_name="api_places",
                        error_type="delivery_error",
                        message=error_message,
                    )
                )

        batch.status = "completed"
        batch.processed_rows = processed
        batch.valid_rows = valid
        batch.invalid_rows = invalid

        db.add_all(errors_to_save)
        db.commit()
    finally:
        db.close()