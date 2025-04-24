from flask import Flask, render_template, request, redirect, url_for, flash
import os
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Paths
PATIENTS_FILE = 'patients.csv'
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure CSV exists
if not os.path.exists(PATIENTS_FILE):
    with open(PATIENTS_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Patient ID", "Name", "Age", "Phone", "Image"])

@app.route('/')
def home():
    return redirect(url_for('patient_entry'))

@app.route('/entry')
def patient_entry():
    return render_template('patient_entry.html')

@app.route('/submit_patient', methods=['POST'])
def submit_patient():
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

    flash("Patient details submitted successfully!", "success")
    return redirect(url_for('patient_entry'))

@app.route('/patients')
def view_patients():
    patients = []
    with open(PATIENTS_FILE, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            patients.append(row)
    return render_template('patients.html', patients=patients)

@app.route('/edit_patient/<patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
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
