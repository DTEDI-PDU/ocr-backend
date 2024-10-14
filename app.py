import os
import camelot
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from database_model import WellReport, db
from cleaning_module import cleaning_profile  # Import your cleaning function

app = Flask(__name__)   
app.config['UPLOAD_FOLDER'] = r'C:\Users\zidan\OneDrive\Documents\UNIVERSITAS GADJAH MADA\PDU\uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:user@localhost/OCR'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


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

            # Clean the profile data from the first table
            profile_data = cleaning_profile(tables[0].df)

            # Insert the extracted data into the database
            new_report = WellReport(
                operator=profile_data.get('operator', ''),
                contractor=profile_data.get('contractor', ''),
                report_no=profile_data.get('report_no', ''),
                well_pad_name=profile_data.get('well_pad_name', ''),
                field=profile_data.get('field', ''),
                well_type_profile=profile_data.get('well_type_profile', ''),
                latitude_longitude=profile_data.get('latitude_longitude', ''),
                environment=profile_data.get('environment', ''),
                gl_msl_m=profile_data.get('gl_msl_m', '')
            )

            db.session.add(new_report)
            db.session.commit()

            return jsonify({'message': 'Well report added successfully!', 'data': profile_data}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Failed to process the PDF: {str(e)}'}), 500

    return jsonify({'message': 'Invalid file type, please upload a PDF file'}), 400

if __name__ == '__main__':
    app.run(debug=True)