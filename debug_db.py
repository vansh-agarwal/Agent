
import sqlite3
import os
import json

db_path = "tasks.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check tasks
print("\n=== TASKS ===")
try:
    cursor.execute("SELECT id, title, user_email, status, created_at FROM tasks ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    if not rows:
        print("No tasks found.")
    for row in rows:
        print(dict(row))
except Exception as e:
    print(f"Error querying tasks: {e}")

# Check oauth tokens
print("\n=== OAUTH TOKENS ===")
try:
    cursor.execute("SELECT user_email, token_expiry FROM oauth_tokens")
    rows = cursor.fetchall()
    if not rows:
        print("No tokens found.")
    for row in rows:
        print(dict(row))
except Exception as e:
    print(f"Error querying tokens: {e}")

# Check if table has correct columns
print("\n=== SCHEMA ===")
cursor.execute("PRAGMA table_info(tasks)")
columns = cursor.fetchall()
for col in columns:
    print(f"{col['name']} ({col['type']})")

conn.close()
