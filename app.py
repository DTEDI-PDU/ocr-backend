import os
import camelot
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from database_model import Profile, GeneralData, DrillingParameter, db
from cleaning_module import cleaning_profile, cleaning_general, cleaning_drilling_parameter

app = Flask(__name__)   
app.config['UPLOAD_FOLDER'] = r'C:\Users\zidan\OneDrive\Documents\UNIVERSITAS GADJAH MADA\PDU\uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:user@localhost/OCR'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()    
    try:
        db.session.execute('SELECT 1')
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {str(e)}")

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

            profile_data = cleaning_profile(tables[0].df)
            general_data = cleaning_general(tables[0].df)
            drilling_data = cleaning_drilling_parameter(tables[0].df)

            # Insert the extracted data into the database
            new_profile = Profile(
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
            new_general_data = GeneralData(
                rig_type_name=general_data.get('rig_type_name', ''),
                rig_power=general_data.get('rig_power', ''),
                kb_elevation=general_data.get('kb_elevation', ''),
                midnight_depth=general_data.get('midnight_depth', ''),
                progress=general_data.get('progress', ''),
                proposed_td=general_data.get('proposed_td', ''),
                spud_date=general_data.get('spud_date', ''),
                release_date=general_data.get('release_date', ''),
                planned_days=general_data.get('planned_days', ''),
                days_from_rig_release=general_data.get('days_from_rig_release', '')
            )

            # Insert drilling parameters data into 'DrillingParameter' table
            new_drilling_data = DrillingParameter(
                average_wob_24_hrs=drilling_data.get('average_wob_24_hrs', ''),
                average_rop_24_hrs=drilling_data.get('average_rop_24_hrs', ''),
                average_surface_rpm_dhm=drilling_data.get('average_surface_rpm_dhm', ''),
                on_off_bottom_torque=drilling_data.get('on_off_bottom_torque', ''),
                flowrate_spp=drilling_data.get('flowrate_spp', ''),
                air_rate=drilling_data.get('air_rate', ''),
                corr_inhib_foam_rate=drilling_data.get('corr_inhib_foam_rate', ''),
                puw_sow_rotw=drilling_data.get('puw_sow_rotw', ''),
                total_drilling_time=drilling_data.get('total_drilling_time', ''),
                ton_miles=drilling_data.get('ton_miles', '')
            )

            db.session.add(new_profile)
            db.session.add(new_general_data)
            db.session.add(new_drilling_data)
            db.session.commit()

            return jsonify({
                'message': 'Reports added successfully!',
                'profile_data': profile_data,
                'general_data': general_data,
                'drilling_data': drilling_data,
            }), 201


        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Failed to process the PDF: {str(e)}'}), 500

    return jsonify({'message': 'Invalid file type, please upload a PDF file'}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all tables
    app.run(debug=True)