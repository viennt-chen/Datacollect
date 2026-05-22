"""
Migration: Add unique index on start_code in event_data table
Run: python migrations/add_start_code_unique_index.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.config import settings


def migrate():
    print("=" * 60)
    print("Add unique index on event_data.start_code")
    print("=" * 60)

    engine = create_engine(settings.DATABASE_URL, echo=False)

    with engine.connect() as conn:
        try:
            # Check if index already exists
            check_sql = """
            SELECT COUNT(*)
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'event_data'
            AND INDEX_NAME = 'idx_start_code'
            """
            result = conn.execute(text(check_sql))
            count = result.scalar()

            if count > 0:
                print("  [SKIP] Index idx_start_code already exists")
            else:
                # Check for duplicate start_code values
                check_duplicates = """
                SELECT start_code, COUNT(*) as cnt
                FROM event_data
                WHERE start_code IS NOT NULL AND start_code != ''
                GROUP BY start_code
                HAVING COUNT(*) > 1
                """
                duplicates = conn.execute(text(check_duplicates)).fetchall()

                if duplicates:
                    print(f"  [WARN] Found {len(duplicates)} duplicate start_code groups, cleaning up...")
                    # Keep the record with the smallest id, delete the rest
                    cleanup_sql = """
                    DELETE e1 FROM event_data e1
                    INNER JOIN (
                        SELECT MIN(id) as min_id, start_code
                        FROM event_data
                        WHERE start_code IS NOT NULL AND start_code != ''
                        GROUP BY start_code
                        HAVING COUNT(*) > 1
                    ) e2 ON e1.start_code = e2.start_code
                        AND e1.id > e2.min_id
                    """
                    result = conn.execute(text(cleanup_sql))
                    conn.commit()
                    print(f"  [OK] Cleaned up {result.rowcount} duplicate records")

                # Add unique index
                create_index_sql = """
                CREATE UNIQUE INDEX idx_start_code ON event_data (start_code)
                """
                conn.execute(text(create_index_sql))
                conn.commit()
                print("  [OK] Unique index idx_start_code created")

            print("\n" + "=" * 60)
            print("Done!")
            print("=" * 60)

        except Exception as e:
            conn.rollback()
            print(f"\n[ERROR] Migration failed: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == '__main__':
    migrate()
