import os
import camelot
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from database_model import Profile, GeneralData, DrillingParameter, AFE, PersonnelInCharge, Summary, TimeBreakdown, db
from cleaning_module import cleaning_data_geo_dipa_energi 
from flask_cors import CORS


app = Flask(__name__)   
app.config['UPLOAD_FOLDER'] = r'C:\Users\zidan\OneDrive\Documents\UNIVERSITAS GADJAH MADA\PDU\uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:user@localhost/OCR'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

db.init_app(app)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and file.filename.endswith('.pdf'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(file_path)
        
        try:
            # Extract tables from the uploaded PDF using Camelot
            tables = camelot.read_pdf(file_path)

            if len(tables) == 0:
                return jsonify({'message': 'No tables found in the PDF file'}), 400

            profile, general, drilling_parameter, afe, personnel_in_charge, summary, time_breakdown = cleaning_data_geo_dipa_energi(tables[0].df)

            # Save the extracted data into the database
            profile_data = Profile(**profile)
            general_data = GeneralData(**general)
            drilling_data = DrillingParameter(**drilling_parameter)
            afe_data = AFE(**afe)
            personnel_data = PersonnelInCharge(**personnel_in_charge)
            summary_data = Summary(**summary)
            time_breakdown_data = TimeBreakdown(**time_breakdown)
        
            db.session.add(profile_data)
            db.session.add(general_data)
            db.session.add(drilling_data)
            db.session.add(afe_data)
            db.session.add(personnel_data)
            db.session.add(summary_data)
            db.session.add(time_breakdown_data)
            db.session.commit()

            return jsonify({
                'message': 'Reports added successfully!',
                'profile_data': profile,
                'general': general,
                'drilling_parameter': drilling_parameter,
                'afe': afe_data.to_dict(),          
                'personnel_data' : personnel_data.to_dict(),
                'summary_data': summary_data.to_dict(),
                'time_breakdown' : time_breakdown_data.to_dict(),
            }), 201


        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Failed to process the PDF: {str(e)}'}), 500

    return jsonify({'message': 'Invalid file type, please upload a PDF file'}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all tables
    app.run(debug=True)