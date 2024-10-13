#code sementara untuk testing import json hasil cleaning ke database dan get json dari database
#masih berjalan pada local

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)

# Configure the PostgreSQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:user@localhost/OCR'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure file upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the database
db = SQLAlchemy(app)

# Define a model for well reports
class WellReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operator = db.Column(db.String(100), nullable=False)
    contractor = db.Column(db.String(100), nullable=False)
    report_no = db.Column(db.String(50), nullable=False)
    well_pad_name = db.Column(db.String(100), nullable=False)
    field = db.Column(db.String(100), nullable=False)
    well_type_profile = db.Column(db.String(100), nullable=False)
    latitude_longitude = db.Column(db.String(100), nullable=False)
    environment = db.Column(db.String(50), nullable=False)
    gl_msl_m = db.Column(db.String(50), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Route to import a JSON file
@app.route('/import_json', methods=['POST'])
def import_json():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if file and file.filename.endswith('.json'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            try:
                data = json.load(json_file)

                # Extract data from the JSON and create a new WellReport instance
                operator = data.get('operator')
                contractor = data.get('contractor')
                report_no = data.get('report_no')
                well_pad_name = data.get('well_pad_name')
                field = data.get('field')
                well_type_profile = data.get('well_type_profile')
                latitude_longitude = data.get('latitude_longitude')
                environment = data.get('environment')
                gl_msl_m = data.get('gl_msl_m')

                new_report = WellReport(
                    operator=operator,
                    contractor=contractor,
                    report_no=report_no,
                    well_pad_name=well_pad_name,
                    field=field,
                    well_type_profile=well_type_profile,
                    latitude_longitude=latitude_longitude,
                    environment=environment,
                    gl_msl_m=gl_msl_m
                )

                db.session.add(new_report)
                db.session.commit()

                return jsonify({'message': 'Well report added successfully!'}), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({'message': f'Failed to add well report: {str(e)}'}), 500

    return jsonify({'message': 'Invalid file type, please upload a JSON file'}), 400

@app.route('/get_well_reports', methods=['GET'])
def get_well_reports():
    try:
        # Query all well reports from the database
        reports = WellReport.query.all()
        
        # Format the result as a list of dictionaries
        well_reports_list = [{
            'id': report.id,
            'operator': report.operator,
            'contractor': report.contractor,
            'report_no': report.report_no,
            'well_pad_name': report.well_pad_name,
            'field': report.field,
            'well_type_profile': report.well_type_profile,
            'latitude_longitude': report.latitude_longitude,
            'environment': report.environment,
            'gl_msl_m': report.gl_msl_m
        } for report in reports]
        
        # Return the result as JSON
        return jsonify(well_reports_list), 200

    except Exception as e:
        return jsonify({'message': f'Failed to retrieve well reports: {str(e)}'}), 500


if __name__ == '__main__':
    # Ensure the upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
