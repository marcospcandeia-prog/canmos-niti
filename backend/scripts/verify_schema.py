"""
Script to verify database schema after migration
"""

import asyncio
from sqlalchemy import text

from app.core.database.session import engine


async def verify_schema():
    """Verify that all tables were created correctly"""
    
    expected_tables = [
        'users',
        'user_profiles',
        'documents',
        'ocr_results',
        'tax_events',
        'declarations',
        'validations',
        'ai_interactions',
        'audit_logs',
    ]
    
    async with engine.connect() as conn:
        # Get list of tables
        result = await conn.execute(
            text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
        )
        
        existing_tables = [row[0] for row in result]
        
        print("=" * 60)
        print("DATABASE SCHEMA VERIFICATION")
        print("=" * 60)
        print(f"\nExpected tables: {len(expected_tables)}")
        print(f"Found tables: {len(existing_tables)}")
        print()
        
        # Check each expected table
        missing_tables = []
        for table in expected_tables:
            if table in existing_tables:
                print(f"✓ {table}")
            else:
                print(f"✗ {table} (MISSING)")
                missing_tables.append(table)
        
        # Check for unexpected tables
        extra_tables = [t for t in existing_tables if t not in expected_tables and t != 'alembic_version']
        if extra_tables:
            print(f"\nUnexpected tables found: {extra_tables}")
        
        # Summary
        print("\n" + "=" * 60)
        if not missing_tables:
            print("✓ ALL TABLES CREATED SUCCESSFULLY")
        else:
            print(f"✗ MISSING TABLES: {missing_tables}")
        print("=" * 60)
        
        # Count rows in each table
        print("\nTable Row Counts:")
        print("-" * 60)
        for table in existing_tables:
            if table != 'alembic_version':
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"{table:20} : {count:>5} rows")
        
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(verify_schema())
