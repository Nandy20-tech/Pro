from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('data/patients.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.before_first_request
def create_tables():
    os.makedirs('data', exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        age INTEGER,
                        phone TEXT,
                        image_path TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except:
            return "User already exists"
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password)).fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    patients = conn.execute('SELECT * FROM patients').fetchall()
    conn.close()
    return render_template('dashboard.html', patients=patients)

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        phone = request.form['phone']
        file = request.files['image']
        image_path = ""
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(image_path)
        conn = get_db_connection()
        conn.execute('INSERT INTO patients (name, age, phone, image_path) VALUES (?, ?, ?, ?)',
                     (name, age, phone, image_path))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('add_patient.html')

@app.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id=?', (id,)).fetchone()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        phone = request.form['phone']
        conn.execute('UPDATE patients SET name=?, age=?, phone=? WHERE id=?', (name, age, phone, id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('edit_patient.html', patient=patient)

@app.route('/view_patient/<int:id>')
def view_patient(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id=?', (id,)).fetchone()
    conn.close()
    return render_template('view_patient.html', patient=patient)

if __name__ == '__main__':
    app.run(debug=True)
