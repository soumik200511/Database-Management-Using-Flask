import MySQLdb

db = MySQLdb.connect(host="localhost", user="root", passwd="soumik@2005", db="student_portal")
cursor = db.cursor()

# List of new columns to add
new_columns = [
    ("contact_number", "VARCHAR(15)"),
    ("address", "TEXT"),
    ("profile_photo", "VARCHAR(255)")
]

for col_name, col_type in new_columns:
    try:
        cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};")
        print(f"✅ Successfully added column: {col_name}")
    except MySQLdb.OperationalError as e:
        # Error 1060 is "Duplicate column name", meaning it already exists!
        if e.args[0] == 1060:
            print(f"⚡ Column '{col_name}' already exists, skipping.")
        else:
            print(f"❌ Error adding {col_name}: {e}")

db.commit()
db.close()
print("Database update complete!")