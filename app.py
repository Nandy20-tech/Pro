from flask import Flask, render_template, request, redirect, url_for, session
import os
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATA_FILE = 'patients.csv'
UPLOAD_FOLDER = 'patients'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure CSV file exists
def initialize_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Name', 'Age', 'Phone', 'Image'])

initialize_csv()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        passkey = request.form.get('passkey')
        if passkey == 'admin123':
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        patient_id = request.form.get('id')
        name = request.form.get('name')
        age = request.form.get('age')
        phone = request.form.get('phone')
        image = request.files['image']
        
        image_path = ''
        if image:
            image_path = os.path.join(UPLOAD_FOLDER, f'{patient_id}_{image.filename}')
            image.save(image_path)
        
        with open(DATA_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([patient_id, name, age, phone, image_path])
        
        return redirect(url_for('dashboard'))
    
    return render_template('add_patient.html')

@app.route('/view_patients')
def view_patients():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    patients = []
    with open(DATA_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            patients.append(row)
    
    return render_template('view_patients.html', patients=patients)

@app.route('/edit_patient/<patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    patients = []
    with open(DATA_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            patients.append(row)
    
    patient = next((p for p in patients if p['ID'] == patient_id), None)
    
    if request.method == 'POST':
        patient['Name'] = request.form.get('name')
        patient['Age'] = request.form.get('age')
        patient['Phone'] = request.form.get('phone')
        
        with open(DATA_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['ID', 'Name', 'Age', 'Phone', 'Image'])
            writer.writeheader()
            writer.writerows(patients)
        
        return redirect(url_for('view_patients'))
    
    return render_template('edit_patient.html', patient=patient)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
