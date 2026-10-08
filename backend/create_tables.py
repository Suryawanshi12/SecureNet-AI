from backend.db import engine, Base
from backend.auth.models import User
from backend.detection.models import Detection  # noqa: F401 – registers table with Base
from sqlalchemy import text

MIGRATION_COLUMNS = [
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS shap_values JSON",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS source_ip VARCHAR(45)",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS destination_ip VARCHAR(45)",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS source_port INTEGER",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS destination_port INTEGER",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS protocol VARCHAR(10)",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS flow_duration_us FLOAT",
    "ALTER TABLE detections ADD COLUMN IF NOT EXISTS packet_count INTEGER",
]

try:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        for sql in MIGRATION_COLUMNS:
            conn.execute(text(sql))
        conn.commit()
    print("✅ Database tables created and migrated successfully!")

except Exception as e:
    print("❌ Failed to create/migrate tables!")
    print("Error:", e)