from backend.db import engine
from sqlalchemy import text

NEW_COLUMNS = [
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS shap_values JSON",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS source_ip VARCHAR(45)",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS destination_ip VARCHAR(45)",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS source_port INTEGER",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS destination_port INTEGER",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS protocol VARCHAR(10)",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS flow_duration_us FLOAT",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS packet_count INTEGER",
]

with engine.connect() as conn:
    for sql in NEW_COLUMNS:
        conn.execute(text(sql))
        print(f"  OK: {sql}")
    conn.commit()
    print("\nMigration complete.")

with engine.connect() as conn:
    rows = conn.execute(text(
        "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='detections' ORDER BY ordinal_position"
    ))
    print("\nCurrent detections table schema:")
    for row in rows:
        print(f"  {row[0]:30s} {row[1]}")
