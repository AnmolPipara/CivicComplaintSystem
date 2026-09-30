"""
JanSewa Database Migration Tool
Imports your complete local database (users, complaints, coordinates, votes, status history)
into your new remote PostgreSQL database on Render, Supabase, or Neon.

Usage:
    python migrate_to_remote_db.py "<YOUR_RENDER_EXTERNAL_DATABASE_URL>"

Example:
    python migrate_to_remote_db.py "postgresql://civic_user:password@dpg-xxxxx.singapore-postgres.render.com/civic_complaints"
"""
import sys
import subprocess
import os

def migrate(remote_db_url: str):
    sql_file = os.path.join(os.path.dirname(__file__), "backup_civic_db.sql")
    if not os.path.exists(sql_file):
        print(f"[ERROR] Backup file not found: {sql_file}")
        sys.exit(1)

    print("=" * 65)
    print("JANSEWA DATABASE MIGRATION TO RENDER / REMOTE POSTGRESQL")
    print("=" * 65)
    print(f"Source Backup: {sql_file} ({os.path.getsize(sql_file) / 1024:.1f} KB)")
    print(f"Target Database: {remote_db_url.split('@')[-1] if '@' in remote_db_url else 'Remote DB'}")
    print("\nStarting migration...")

    # Method 1: Use psql inside civic-postgres Docker container (guaranteed to have PostgreSQL client)
    try:
        with open(sql_file, "rb") as f:
            proc = subprocess.run(
                ["docker", "exec", "-i", "civic-postgres", "psql", remote_db_url],
                stdin=f,
                capture_output=True,
                text=True
            )
            if proc.returncode == 0:
                print("\n[SUCCESS] All tables, complaints, users, votes, and history migrated successfully!")
                print("Your remote database now has the exact same data as your local machine.")
                return
            else:
                print(f"[WARN] Docker psql returned code {proc.returncode}: {proc.stderr[:300]}")
    except Exception as e:
        print(f"[INFO] Docker psql execution failed ({e}), attempting local psql...")

    # Method 2: Fallback to local psql
    try:
        with open(sql_file, "rb") as f:
            proc2 = subprocess.run(
                ["psql", remote_db_url],
                stdin=f,
                capture_output=True,
                text=True
            )
            if proc2.returncode == 0:
                print("\n[SUCCESS] All data migrated successfully via local psql!")
                return
            else:
                print(f"[ERROR] Migration failed: {proc2.stderr}")
    except FileNotFoundError:
        print("\n[ERROR] Neither docker nor psql was able to execute the command directly.")
        print("You can run the following command directly in PowerShell or Terminal:")
        print(f'Get-Content backup_civic_db.sql | docker exec -i civic-postgres psql "{remote_db_url}"')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_remote_db.py \"<YOUR_RENDER_EXTERNAL_DATABASE_URL>\"")
        sys.exit(1)
    migrate(sys.argv[1])
