from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import csv

app = Flask(__name__)
app.secret_key = 'Nandhu@20'

# File Paths
PATIENTS_FILE = 'patients.csv'
UPLOAD_FOLDER = 'static/uploads'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure CSV file exists
if not os.path.exists(PATIENTS_FILE):
    with open(PATIENTS_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Patient ID", "Name", "Age", "Phone", "Image"])

# Dummy user for login
users = {'Nandhitha': 'Nandhu20'}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        session['username'] = username
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials!', 'danger')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('index'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/add_patient')
def add_patient():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('add_patient.html')

@app.route('/submit_patient', methods=['POST'])
def submit_patient():
    if 'username' not in session:
        return redirect(url_for('index'))

    name = request.form['name']
    patient_id = request.form['patient_id']
    age = request.form['age']
    phone = request.form['phone']
    image = request.files['image']

    image_filename = None
    if image and image.filename:
        image_filename = os.path.join(UPLOAD_FOLDER, f"{patient_id}_{image.filename}")
        image.save(image_filename)

    with open(PATIENTS_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([patient_id, name, age, phone, image_filename])

    flash("Patient details submitted successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/patients')
def view_patients():
    if 'username' not in session:
        return redirect(url_for('index'))

    patients = []
    with open(PATIENTS_FILE, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            patients.append(row)
    return render_template('patients.html', patients=patients)

@app.route('/edit_patient/<patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    if 'username' not in session:
        return redirect(url_for('index'))

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
        updated_name = request.form['name']
        updated_age = request.form['age']
        updated_phone = request.form['phone']

        for p in patients:
            if p[0] == patient_id:
                p[1] = updated_name
                p[2] = updated_age
                p[3] = updated_phone
                break

        with open(PATIENTS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(patients)

        flash("Patient details updated successfully!", "success")
        return redirect(url_for('view_patients'))

    return render_template('edit_patient.html', patient=patient)

if __name__ == '__main__':
    app.run(debug=True)
