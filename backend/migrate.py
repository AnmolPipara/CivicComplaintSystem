import asyncio
from sqlalchemy import text
from db.session import SessionLocal

def migrate():
    db = SessionLocal()
    try:
        # Alter complaints table
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS location VARCHAR(255);"))
        
        # Populate location with dummy data for now so we don't violate NOT NULL if we add it
        db.execute(text("UPDATE complaints SET location = 'Default Location' WHERE location IS NULL;"))
        db.execute(text("ALTER TABLE complaints ALTER COLUMN location SET NOT NULL;"))
        
        db.execute(text("ALTER TABLE complaints DROP COLUMN IF EXISTS location_id;"))
        db.execute(text("ALTER TABLE complaints DROP COLUMN IF EXISTS cluster_id;"))
        db.execute(text("ALTER TABLE complaints DROP COLUMN IF EXISTS priority;"))
        db.execute(text("ALTER TABLE complaints DROP COLUMN IF EXISTS priority_score;"))
        
        # Change status enum to varchar
        db.execute(text("ALTER TABLE complaints ALTER COLUMN status TYPE VARCHAR;"))
        
        # Update existing statuses
        db.execute(text("UPDATE complaints SET status = 'pending' WHERE status IN ('submitted', 'prioritized');"))
        db.execute(text("UPDATE complaints SET status = 'working' WHERE status IN ('assigned', 'in_progress');"))
        db.execute(text("UPDATE complaints SET status = 'completed' WHERE status IN ('resolved', 'rejected');"))
        
        # Change complaint_status_history enum to varchar
        db.execute(text("ALTER TABLE complaint_status_history ALTER COLUMN previous_status TYPE VARCHAR;"))
        db.execute(text("ALTER TABLE complaint_status_history ALTER COLUMN new_status TYPE VARCHAR;"))
        
        # Drop unused tables
        db.execute(text("DROP TABLE IF EXISTS locations CASCADE;"))
        db.execute(text("DROP TABLE IF EXISTS clusters CASCADE;"))
        db.execute(text("DROP TABLE IF EXISTS notifications CASCADE;"))
        
        db.commit()
        print("Migration successful")
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
