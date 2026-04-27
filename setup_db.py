import MySQLdb

# 1. Connect to MySQL Server (without selecting a database yet)
# NOTE: Make sure 'password' matches your actual MySQL root password.
# If you have no password, leave it as ""
try:
    db = MySQLdb.connect(host="localhost", user="root", passwd="soumik@2005")
    cursor = db.cursor()

    # 2. Create the Database
    cursor.execute("CREATE DATABASE IF NOT EXISTS student_portal")
    print("Database 'student_portal' created successfully.")

    # 3. Select the Database
    db.select_db("student_portal")

    # 4. Create Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        full_name VARCHAR(100),
        email VARCHAR(100)
    )
    """)
    print("Table 'users' created successfully.")

    # 5. Create Grades Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS grades (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        subject VARCHAR(50),
        marks INT,
        grade CHAR(2),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    print("Table 'grades' created successfully.")
    
    db.commit()
    db.close()
    
except MySQLdb.OperationalError as e:
    if e.args[0] == 1045:
        print("❌ ERROR: Access Denied. Please check the 'passwd' field in this script matches your MySQL installation.")
    else:
        print(f"❌ Error: {e}")