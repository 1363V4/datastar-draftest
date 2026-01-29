"""
Migration Strategy: Old Draft schema -> New normalized schema

Approach: Online migration with dual-write period to avoid downtime
"""

from peewee import PostgresqlDatabase, Model, SQL
import logging

logger = logging.getLogger(__name__)

# Constants
TEAM_BLUE = 0
TEAM_RED = 1
TYPE_BAN = 0
TYPE_PICK = 1


def create_new_tables(db):
    """Step 1: Create new tables alongside old ones"""
    # SQLite doesn't support multiple statements in one execute
    # Also: INTEGER PRIMARY KEY = AUTOINCREMENT, TEXT for UUIDs, no SERIAL

    db.execute_sql("""
        CREATE TABLE IF NOT EXISTS drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            blue_player TEXT NOT NULL,
            red_player TEXT,
            current_move INTEGER NOT NULL DEFAULT 0,
            votes_blue INTEGER NOT NULL DEFAULT 1,
            votes_red INTEGER NOT NULL DEFAULT 1
        )
    """)

    db.execute_sql("""
        CREATE TABLE IF NOT EXISTS picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draft_id INTEGER NOT NULL,
            team INTEGER NOT NULL,
            pick_type INTEGER NOT NULL,
            pick_order INTEGER NOT NULL,
            champion_id INTEGER,
            FOREIGN KEY (draft_id) REFERENCES drafts(id) ON DELETE CASCADE
        )
    """)

    db.execute_sql("""
        CREATE INDEX IF NOT EXISTS idx_picks_draft_id
        ON picks(draft_id, id)
    """)

    db.execute_sql("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_picks_unique
        ON picks(draft_id, team, pick_type, pick_order)
    """)

    db.execute_sql("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            draft_id INTEGER NOT NULL,
            FOREIGN KEY (draft_id) REFERENCES drafts(id) ON DELETE CASCADE
        )
    """)

    db.execute_sql("""
        CREATE INDEX IF NOT EXISTS idx_votes_draft
        ON votes(draft_id)
    """)

    db.execute_sql("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_votes_unique
        ON votes(user_id, draft_id)
    """)

    logger.info("New tables created")


def migrate_existing_data(db):
    """Step 2: Copy data from old Draft table to new schema"""

    # Map old column names to (team, pick_type, pick_order)
    pick_mapping = [
        ('r1b', TEAM_RED, TYPE_BAN, 1),
        ('b1b', TEAM_BLUE, TYPE_BAN, 1),
        ('b2b', TEAM_BLUE, TYPE_BAN, 2),
        ('r2b', TEAM_RED, TYPE_BAN, 2),
        ('r3b', TEAM_RED, TYPE_BAN, 3),
        ('b3b', TEAM_BLUE, TYPE_BAN, 3),
        ('b1p', TEAM_BLUE, TYPE_PICK, 1),
        ('r1p', TEAM_RED, TYPE_PICK, 1),
        ('r2p', TEAM_RED, TYPE_PICK, 2),
        ('b2p', TEAM_BLUE, TYPE_PICK, 2),
        ('b3p', TEAM_BLUE, TYPE_PICK, 3),
        ('r3p', TEAM_RED, TYPE_PICK, 3),
        ('r4b', TEAM_RED, TYPE_BAN, 4),
        ('b4b', TEAM_BLUE, TYPE_BAN, 4),
        ('b5b', TEAM_BLUE, TYPE_BAN, 5),
        ('r5b', TEAM_RED, TYPE_BAN, 5),
        ('r4p', TEAM_RED, TYPE_PICK, 4),
        ('b4p', TEAM_BLUE, TYPE_PICK, 4),
        ('b5p', TEAM_BLUE, TYPE_PICK, 5),
        ('r5p', TEAM_RED, TYPE_PICK, 5),
    ]

    with db.atomic():
        # Insert into drafts table
        db.execute_sql("""
            INSERT INTO drafts (id, created, blue_player, red_player, current_move, votes_blue, votes_red)
            SELECT id, created, blue, red, current_move, votes_blue, votes_red
            FROM draft
            ORDER BY id
        """)

        # Build the picks insert for each old draft
        for old_col, team, pick_type, pick_order in pick_mapping:
            db.execute_sql(f"""
                INSERT INTO picks (draft_id, team, pick_type, pick_order, champion_id)
                SELECT id, {team}, {pick_type}, {pick_order}, {old_col}
                FROM draft
                WHERE {old_col} IS NOT NULL
            """)

        # Migrate votes (assuming old Vote.draft_id was the ID)
        db.execute_sql("""
            INSERT INTO votes (user_id, draft_id)
            SELECT user_id, draft_id
            FROM vote
            ON CONFLICT (user_id, draft_id) DO NOTHING
        """)

        logger.info("Data migrated successfully")


def verify_migration(db):
    """Step 3: Verify data integrity"""

    # Check row counts match
    old_count = db.execute_sql("SELECT COUNT(*) FROM draft").fetchone()[0]
    new_count = db.execute_sql("SELECT COUNT(*) FROM drafts").fetchone()[0]

    if old_count != new_count:
        raise Exception(f"Draft count mismatch: {old_count} old vs {new_count} new")

    # Verify a sample of picks were migrated correctly
    sample = db.execute_sql("""
        SELECT d.id, d.b1p, d.r3b
        FROM draft d
        LIMIT 100
    """).fetchall()

    for draft_id, b1p, r3b in sample:
        if b1p:
            result = db.execute_sql("""
                SELECT champion_id FROM picks
                WHERE draft_id = %s AND team = %s AND pick_type = %s AND pick_order = %s
            """, (draft_id, TEAM_BLUE, TYPE_PICK, 1)).fetchone()
            if not result or result[0] != b1p:
                raise Exception(f"Pick mismatch for draft {draft_id}")

        if r3b:
            result = db.execute_sql("""
                SELECT champion_id FROM picks
                WHERE draft_id = %s AND team = %s AND pick_type = %s AND pick_order = %s
            """, (draft_id, TEAM_RED, TYPE_BAN, 3)).fetchone()
            if not result or result[0] != r3b:
                raise Exception(f"Ban mismatch for draft {draft_id}")

    logger.info("Migration verification passed")


def drop_old_tables(db):
    """Step 4: Drop old tables (ONLY after code is updated and tested)"""
    with db.atomic():
        db.execute_sql("DROP TABLE IF EXISTS vote")
        db.execute_sql("DROP TABLE IF EXISTS draft")
    logger.info("Old tables dropped")


def full_migration(db, drop_old=False):
    """
    Complete migration process

    WARNING: Test this on a backup database first!

    Recommended rollout:
    1. Run create_new_tables() and migrate_existing_data() in production
    2. Deploy new code that writes to BOTH old and new schemas
    3. Monitor for 24-48 hours
    4. Deploy code that only uses new schema
    5. After another 24-48 hours, run drop_old_tables()
    """
    try:
        create_new_tables(db)
        migrate_existing_data(db)
        verify_migration(db)

        if drop_old:
            logger.warning("Dropping old tables!")
            drop_old_tables(db)
        else:
            logger.info("Migration complete. Old tables preserved.")
            logger.info("Update your code to use new models, then run with drop_old=True")

        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
        raise


# Example dual-write adapter for transition period
class DualWriteDraft:
    """
    Adapter that writes to both old and new schemas during migration.
    Use this temporarily to ensure zero data loss during rollout.
    """

    @staticmethod
    def create_draft(blue_player, red_player=None):
        from old_models import Draft as OldDraft
        from new_models import Draft as NewDraft, Pick

        # Write to old schema
        old_draft = OldDraft.create(
            blue=blue_player,
            red=red_player
        )

        # Write to new schema
        new_draft = NewDraft.create(
            id=old_draft.id,  # Keep same ID
            blue_player=blue_player,
            red_player=red_player
        )

        # Initialize picks
        from new_models import initialize_draft_picks
        initialize_draft_picks(new_draft)

        return old_draft.id

    @staticmethod
    def make_pick(draft_id, champion_id, move_index):
        from old_models import Draft as OldDraft
        from new_models import Draft as NewDraft, Pick

        # This would need the column mapping logic
        # Left as exercise - depends on your move_index interpretation

        pass


if __name__ == "__main__":
    # Example usage
    from peewee import SqliteDatabase

    db = SqliteDatabase('drafts.db')

    # IMPORTANT: Enable foreign keys in SQLite
    db.execute_sql('PRAGMA foreign_keys = ON')

    # Test on backup first!
    full_migration(db, drop_old=False)
