"""
Database migration script to add latitude and longitude to citizens table.
"""
from sqlalchemy import text
from db.session import SessionLocal

def run_migration():
    db = SessionLocal()
    try:
        print("Checking citizens table schema...")
        db.execute(text("ALTER TABLE citizens ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION;"))
        db.execute(text("ALTER TABLE citizens ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION;"))
        db.commit()
        print("Successfully added latitude and longitude to citizens table.")
    except Exception as e:
        db.rollback()
        print("Migration failed:", e)
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
