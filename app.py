from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERS_FILE = 'users.csv'
PATIENTS_FILE = 'patients.csv'

# Ensure files exist
for filename in [USERS_FILE, PATIENTS_FILE]:
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            if 'user' in filename:
                writer.writerow(['username', 'password'])
            else:
                writer.writerow(['Patient ID', 'Name', 'Age', 'Phone', 'Image'])

@app.route('/')
def index():
    return render_template('index.html')

# ── Register ──────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with open(USERS_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, password])
        flash('Registered successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# ── Login ──────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with open(USERS_FILE, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if row[0] == username and row[1] == password:
                    session['user'] = username
                    return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── Dashboard ──────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# ── Add Patient ──────────────────────────────
@app.route('/add_patient')
def add_patient():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('add_patient.html')

@app.route('/submit_patient', methods=['POST'])
def submit_patient():
    if 'user' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    patient_id = request.form['patient_id']
    age = request.form['age']
    phone = request.form['phone']
    image = request.files['image']

    image_filename = ""
    if image and image.filename:
        image_filename = os.path.join(UPLOAD_FOLDER, f"{patient_id}_{image.filename}")
        image.save(image_filename)

    with open(PATIENTS_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([patient_id, name, age, phone, image_filename])

    flash('Patient added!', 'success')
    return redirect(url_for('dashboard'))

# ── View Patients ──────────────────────────────
@app.route('/patients')
def view_patients():
    if 'user' not in session:
        return redirect(url_for('login'))

    patients = []
    with open(PATIENTS_FILE, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            patients.append(row)
    return render_template('patients.html', patients=patients)

# ── Edit Patient ──────────────────────────────
@app.route('/edit_patient/<patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    patients = []
    with open(PATIENTS_FILE, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        for row in reader:
            patients.append(row)

    patient = next((p for p in patients if p[0] == patient_id), None)
    if not patient:
        flash("Patient not found!", "danger")
        return redirect(url_for('view_patients'))

    if request.method == 'POST':
        patient[1] = request.form['name']
        patient[2] = request.form['age']
        patient[3] = request.form['phone']

        with open(PATIENTS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(patients)

        flash("Updated successfully", "success")
        return redirect(url_for('view_patients'))

    return render_template('edit_patient.html', patient=patient)

if __name__ == '__main__':
    app.run(debug=True)
