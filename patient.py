from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(120), nullable=False)
    admission = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.Integer, nullable=False)


@app.route('/v1/patients/', methods=['GET'])
def get_all_patients():
    try:
        patients = Patient.query.all()
        patients_list = [
            {
                'id': patient.id,
                'name': patient.name,
                'age': patient.age,
                'address': patient.address,
                'admission': patient.admission,
                'phone': patient.phone
            }
            for patient in patients
        ]
        return jsonify({'patients': patients_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/v1/patients', methods=['POST'])
def add_patient():
    data = request.get_json()
    new_patient = Patient(name=data['name'], age=data['age'], address=data['address'], admission=data['admission'], phone=data['phone'])
    db.session.add(new_patient)
    db.session.commit()
    return jsonify({'message': 'Patient added successfully'}), 201

@app.route('/v1/patients/<int:id>', methods=['GET'])
def get_patient(id):
    patient = Patient.query.get_or_404(id)
    return jsonify({'id': patient.id,'name': patient.name, 'age': patient.age, 'address': patient.address, 'admission':patient.admission, 'phone':patient.phone})

    
@app.route('/v1/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        data = request.json
        if 'phone' in data:
            patient.phone = data['phone']
        if 'address' in data:
            patient.address = data['address']
        if 'admission' in data:
            patient.admission = data['admission']
        db.session.commit()
        
        return jsonify({'message': 'Patient updated successfully', 'patient': {
            'name': patient.name,
            'age': patient.age,
            'address': patient.address,
            'admission': patient.admission,
            'phone': patient.phone
        }}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# @app.route('/v1/patients/<int:id>', methods=['DELETE'])
# def delete_doctor(id):
#     try:
#         patient = Patient.query.get(id)
#         if not patient:
#             return jsonify({'error': 'Patient not found'}), 404

#         db.session.delete(patient)
#         db.session.commit()

#         return jsonify({'message': f'Patient with ID {id} has been deleted successfully'}), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@app.route('/v1/patients/search', methods=['GET'])
def search_patient_by_name():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({'error': 'name query parameter is required'}), 400
        
        patients = Patient.query.filter(Patient.name.ilike(f"%{name}%")).all()

        if not patients:
            return jsonify({'message': f'No Patient found with "{name}"'}), 404

        patient_list = [
            {
            'id' : patient.id,
            'name': patient.name,
            'age': patient.age,
            'address': patient.address,
            'admission': patient.admission,
            'phone': patient.phone
            }
            for patient in patients
        ]
        return jsonify({'patients': patient_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
port = int(os.getenv('FLASK_PORT',5001)) 
if __name__ == '__main__':    
    app.run(host='127.0.0.1', port=port, debug=True)