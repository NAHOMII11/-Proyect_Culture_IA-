CREATE TABLE IF NOT EXISTS import_batches (
    id VARCHAR PRIMARY KEY,
    status VARCHAR NOT NULL DEFAULT 'processing',
    processed_rows INTEGER NOT NULL DEFAULT 0,
    valid_rows INTEGER NOT NULL DEFAULT 0,
    invalid_rows INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS import_errors (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR NOT NULL,
    row_number INTEGER NOT NULL,
    field_name VARCHAR NOT NULL,
    error_type VARCHAR NOT NULL,
    message TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_import_batches_id ON import_batches (id);
CREATE INDEX IF NOT EXISTS ix_import_errors_batch_id ON import_errors (batch_id);