from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import qrcode
import os

app = Flask(__name__)

# MS SQL Server Configuration (Modify with your credentials)
app.config['SQLALCHEMY_DATABASE_URI'] = r"mssql+pyodbc://@LAPTOP-OF9OS0CA\SQLEXPRESS/EmployeeDB?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server"


# For pyodbc (Uncomment if using pyodbc)
#checking the 2nd git push

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Ensure static directory for QR codes exists
QR_FOLDER = "static/qr_codes"
os.makedirs(QR_FOLDER, exist_ok=True)

# Define Employee Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    password = db.Column(db.String(100), nullable=False)  # Hashed Employee ID

# Initialize Database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.form
    emp_id = int(data['id'])
    emp_name = data['name']
    emp_phone = data['phone']
    emp_email = data.get('email', '')
    emergency_contact = data.get('emergency_contact', '')
    emergency_phone = data.get('emergency_phone', '')
    emp_address = data.get('address', '')

    # ✅ Accept user-entered password
    emp_password = data.get('password', str(emp_id))  # Default to ID if no password entered

    new_employee = Employee(
        id=emp_id, name=emp_name, phone=emp_phone, email=emp_email,
        emergency_contact=emergency_contact, emergency_phone=emergency_phone,
        address=emp_address, password=emp_password
    )
    db.session.add(new_employee)
    db.session.commit()

    # Generate QR Code with URL
    
    qr_data = url_for('view_employee', emp_id=emp_id, _external=True)
    qr_path = os.path.join(QR_FOLDER, f"{emp_id}.png")
    qr = qrcode.make(qr_data)
    qr.save(qr_path)

    return render_template('qr_result.html', qr_image=url_for('static', filename=f"qr_codes/{emp_id}.png"), emp_id=emp_id)

@app.route('/employee/<int:emp_id>', methods=['GET', 'POST'])
def view_employee(emp_id):
    employee = Employee.query.get(emp_id)

    if not employee:
        return "Employee not found!", 404

    if request.method == 'POST':
        password = request.form['password']
        if bcrypt.check_password_hash(employee.password, password):
            return render_template('employee_details.html', employee=employee, full_access=True)
        else:
            return "Incorrect password!", 403

    # Show limited data
    return render_template('employee_details.html', employee=employee, full_access=False)

if __name__ == '__main__':
    app.run(debug=True)
