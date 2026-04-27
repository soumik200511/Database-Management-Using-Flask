import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Secret key for session management and flashing messages
app.secret_key = 'your_secret_key_here'

# Configure Upload Folder for Profile Photos
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MySQL Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'soumik@2005'
app.config['MYSQL_DB'] = 'student_portal'

mysql = MySQL(app)

# ----------------------------------------
# Route: Home / Login
# ----------------------------------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            flash('Logged in successfully!')
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect username or password!')
            
    return render_template('login.html')

# ----------------------------------------
# Route: Register
# ----------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        hashed_password = generate_password_hash(password)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account:
            flash('Account already exists!')
        else:
            try:
                cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', 
                               (username, hashed_password, email))
                mysql.connection.commit()
                
                new_user_id = cursor.lastrowid
                default_grades = [
                    (new_user_id, 'Math', 85, 'A'),
                    (new_user_id, 'Science', 92, 'O'),
                    (new_user_id, 'History', 78, 'B'),
                    (new_user_id, 'English', 90, 'O'),
                    (new_user_id, 'Computer Science', 88, 'A')
                ]
                
                cursor.executemany("INSERT INTO grades (user_id, subject, marks, grade) VALUES (%s, %s, %s, %s)", default_grades)
                mysql.connection.commit()
                
                flash('You have successfully registered with default subjects!')
                return redirect(url_for('login'))
                
            except Exception as e:
                flash(f'An error occurred during registration: {str(e)}')
                
    return render_template('register.html')

# ----------------------------------------
# Route: Dashboard
# ----------------------------------------
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM grades WHERE user_id = %s', (session['id'],))
        grades = cursor.fetchall()
        return render_template('dashboard.html', grades=grades, username=session.get('username'))
    
    return redirect(url_for('login'))

# ----------------------------------------
# Route: Profile (Updated to prevent KeyError)
# ----------------------------------------
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch current account info first to know the existing photo
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        
        if request.method == 'POST':
            # Profile Update Form
            if 'email' in request.form:
                full_name = request.form.get('full_name', '')
                email = request.form.get('email', '')
                contact_number = request.form.get('contact_number', '')
                address = request.form.get('address', '')
                
                # SAFE DICTIONARY ACCESS: Using .get() prevents KeyError if the column is missing
                photo_filename = account.get('profile_photo') 
                
                # Process file upload if one was provided
                if 'profile_photo' in request.files:
                    file = request.files['profile_photo']
                    if file and file.filename != '':
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        photo_filename = filename 
                
                cursor.execute('''
                    UPDATE users 
                    SET full_name = %s, email = %s, contact_number = %s, address = %s, profile_photo = %s 
                    WHERE id = %s
                ''', (full_name, email, contact_number, address, photo_filename, session['id']))
                mysql.connection.commit()
                flash('Profile updated successfully!')
                return redirect(url_for('profile'))
            
            # Password Reset Form
            elif 'new_password' in request.form:
                new_password = generate_password_hash(request.form['new_password'])
                cursor.execute('UPDATE users SET password = %s WHERE id = %s', (new_password, session['id']))
                mysql.connection.commit()
                flash('Password updated successfully!')
                return redirect(url_for('profile'))

        return render_template('profile.html', account=account)
        
    return redirect(url_for('login'))

# ----------------------------------------
# Route: Add Grade
# ----------------------------------------
@app.route('/add_grade', methods=['GET', 'POST'])
def add_grade():
    if 'loggedin' in session:
        if request.method == 'POST':
            subject = request.form['subject']
            marks = request.form['marks']
            grade = request.form['grade']
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO grades (user_id, subject, marks, grade) VALUES (%s, %s, %s, %s)', 
                           (session['id'], subject, marks, grade))
            mysql.connection.commit()
            
            flash(f'{subject} added successfully!')
            return redirect(url_for('dashboard'))
            
        return render_template('add_grade.html')
    return redirect(url_for('login'))

# ----------------------------------------
# Route: Logout
# ----------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)