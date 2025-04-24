from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'Nandhu@20'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database helper function
def get_db_connection():
    conn = sqlite3.connect('data/patients.db')
    conn.row_factory = sqlite3.Row
    return conn

# Authentication function
def check_user(username, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user and user['password'] == password

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('patient_dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if check_user(username, password):
        session['username'] = username
        return redirect(url_for('patient_dashboard'))
    return "Invalid credentials", 401

@app.route('/patient_dashboard')
def patient_dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    patients = conn.execute('SELECT * FROM patients').fetchall()
    conn.close()
    return render_template('patient_details.html', patients=patients)

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        phone = request.form['phone']
        file = request.files['image']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            conn = get_db_connection()
            conn.execute('INSERT INTO patients (name, age, phone, image_path) VALUES (?, ?, ?, ?)',
                         (name, age, phone, image_path))
            conn.commit()
            conn.close()

            return redirect(url_for('patient_dashboard'))
    return render_template('index.html')

@app.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    if 'username' not in session:
        return redirect(url_for('index'))

    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        phone = request.form['phone']
        conn.execute('UPDATE patients SET name = ?, age = ?, phone = ? WHERE id = ?',
                     (name, age, phone, id))
        conn.commit()
        conn.close()
        return redirect(url_for('patient_dashboard'))
    
    return render_template('index.html', patient=patient)

if __name__ == '__main__':
    app.run(debug=True)
