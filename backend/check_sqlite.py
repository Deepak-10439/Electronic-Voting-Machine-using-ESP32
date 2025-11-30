"""
Check what's in the SQLite database
"""
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=" * 70)
print("TABLES IN db.sqlite3")
print("=" * 70)
print()

for table in tables:
    table_name = table[0]
    print(f"📋 Table: {table_name}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"   Rows: {count}")
    
    if count > 0:
        # Show column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        print(f"   Columns: {', '.join(col_names)}")
    
    print()

conn.close()

print("=" * 70)
print("WHAT IS db.sqlite3?")
print("=" * 70)
print("""
db.sqlite3 is Django's default local database used for:

1. ✅ Django Admin Panel
   - User accounts (superusers)
   - Admin authentication
   - Session management

2. ✅ Django Built-in Models
   - auth_user (admin users)
   - django_session (login sessions)
   - django_migrations (tracking)
   - auth_permission, auth_group (permissions)

3. ❌ NOT storing your fingerprint data
   - Your fingerprint data is in Firebase
   - This database doesn't touch Firebase data
   - It's only for Django's internal operations

You can safely keep it - it's used for Django admin and authentication!
""")
