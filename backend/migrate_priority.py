import sys
from sqlalchemy import text
from db.session import SessionLocal

def migrate_priority():
    db = SessionLocal()
    try:
        print("Starting priority migration...")
        
        # Add new columns to complaints table
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS severity_score INTEGER;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS impact_score INTEGER;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS urgency_score INTEGER;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS priority_score DOUBLE PRECISION;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS priority_level VARCHAR(20);"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS assessment_status VARCHAR(20) DEFAULT 'pending';"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS assessment_reason TEXT;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS assessment_confidence VARCHAR(20);"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS missing_information JSON;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS needs_human_review BOOLEAN DEFAULT FALSE;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS is_safety_escalated BOOLEAN DEFAULT FALSE;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS ai_severity_score INTEGER;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS ai_impact_score INTEGER;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS ai_urgency_score INTEGER;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS ai_reason TEXT;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS admin_override BOOLEAN DEFAULT FALSE;"))
        db.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS admin_override_reason TEXT;"))
        
        # Create index on priority_score and priority_level for fast sorting and filtering
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_complaints_priority_score ON complaints (priority_score DESC);"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_complaints_priority_level ON complaints (priority_level);"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_complaints_needs_human_review ON complaints (needs_human_review);"))
        
        db.commit()
        print("Priority migration completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"Priority migration failed: {e}", file=sys.stderr)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_priority()
