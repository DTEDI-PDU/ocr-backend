import os
import hashlib
import camelot
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from sqlalchemy.inspection import inspect

from database_model import (
    Profile,
    GeneralData,
    DrillingParameter,
    AFE,
    PersonnelInCharge,
    Summary,
    TimeBreakdown,
    db,
)
from cleaning_module import cleaning_data_geo_dipa_energi
from flask_cors import CORS


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "/app/uploads"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres.rexyqbeqbfbjwkapxgnp:Wicaksono69@@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)

db.init_app(app)


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


def calculate_hash(data_dict):
    data_string = "".join(str(value) for value in data_dict.values())
    return hashlib.md5(data_string.encode()).hexdigest()


def object_to_dict(obj):
    return {
        column.key: getattr(obj, column.key)
        for column in inspect(obj).mapper.column_attrs
    }


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    if file and file.filename.endswith(".pdf"):
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"], secure_filename(file.filename)
        )
        file.save(file_path)

        try:
            # Extract tables from the uploaded PDF using Camelot
            tables = camelot.read_pdf(file_path)

            if len(tables) == 0:
                return jsonify({"message": "No tables found in the PDF file"}), 400

            (
                profile,
                general,
                drilling_parameter,
                afe,
                personnel_in_charge,
                summary,
                time_breakdown,
            ) = cleaning_data_geo_dipa_energi(tables[0].df)

            time_breakdown = {i: entry for i, entry in enumerate(time_breakdown)}

            unique_hash = calculate_hash(profile)
            existing_profile = Profile.query.filter_by(unique_hash=unique_hash).first()
            if existing_profile:
                return (
                    jsonify(
                        {
                            "message": "Data already exists in the database. Upload canceled."
                        }
                    ),
                    409,
                )

            # Save the extracted data into the database
            profile_data = Profile(**profile, unique_hash=unique_hash)
            db.session.add(profile_data)
            db.session.commit()

            general_data = GeneralData(**general, profile_id=profile_data.id)
            drilling_data = DrillingParameter(
                **drilling_parameter, profile_id=profile_data.id
            )
            afe_data = AFE(**afe, profile_id=profile_data.id)
            personnel_data = PersonnelInCharge(
                **personnel_in_charge, profile_id=profile_data.id
            )
            summary_data = Summary(**summary, profile_id=profile_data.id)

            for item in time_breakdown.values():
                time_breakdown_data = TimeBreakdown(
                    start=item["start"],
                    end=item["end"],
                    elapsed=item["elapsed"],
                    depth=item["depth"],
                    pt_npt=item["pt_npt"],
                    code=item["code"],
                    description=item["description"],
                    operation=item["operation"],
                    profile_id=profile_data.id,  # Link to the profile_id
                )
                db.session.add(time_breakdown_data)

            # time_breakdown_data = TimeBreakdown(**time_breakdown, profile_id=profile_data.id)

            db.session.add(general_data)
            db.session.add(drilling_data)
            db.session.add(afe_data)
            db.session.add(personnel_data)
            db.session.add(summary_data)
            # db.session.add_all(time_breakdown_data)
            db.session.commit()

            return (
                jsonify(
                    {
                        "message": "Reports added successfully!",
                        "profile_data": profile,
                        "general": general,
                        "drilling_parameter": drilling_parameter,
                        "afe": afe_data.to_dict(),
                        "personnel_data": personnel_data.to_dict(),
                        "summary_data": summary_data.to_dict(),
                        "time_breakdown": time_breakdown,
                    }
                ),
                201,
            )

        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Failed to process the PDF: {str(e)}"}), 500

    return jsonify({"message": "Invalid file type, please upload a PDF file"}), 400


@app.route("/get_all_data", methods=["GET"])
def fetch_all_tables():
    try:
        # Fetch data from all tables
        profile_data = [object_to_dict(profile) for profile in Profile.query.all()]
        general_data = [object_to_dict(general) for general in GeneralData.query.all()]
        drilling_parameter_data = [
            object_to_dict(drilling_param)
            for drilling_param in DrillingParameter.query.all()
        ]
        afe_data = [object_to_dict(afe) for afe in AFE.query.all()]
        personnel_data = [
            object_to_dict(personnel) for personnel in PersonnelInCharge.query.all()
        ]
        summary_data = [object_to_dict(summary) for summary in Summary.query.all()]
        time_breakdown_data = [
            object_to_dict(time_breakdown)
            for time_breakdown in TimeBreakdown.query.all()
        ]

        # Combine all data
        all_data = {
            "profile": profile_data,
            "general_data": general_data,
            "drilling_parameters": drilling_parameter_data,
            "afe": afe_data,
            "personnel_in_charge": personnel_data,
            "summary": summary_data,
            "time_breakdown": time_breakdown_data,
        }

        return jsonify(all_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/fetch/<int:report_id>", methods=["GET"])
def fetch_report_by_id(report_id):
    try:
        # Fetch data from all tables for the given report ID
        profile_data = Profile.query.get(report_id)
        general_data = GeneralData.query.get(report_id)
        drilling_parameter_data = DrillingParameter.query.get(report_id)
        afe_data = AFE.query.get(report_id)
        personnel_data = PersonnelInCharge.query.get(report_id)
        summary_data = Summary.query.get(report_id)
        time_breakdown_data = TimeBreakdown.query.filter_by(profile_id=report_id).all()

        # Convert to dictionary format for JSON response
        report_data = {
            "profile": object_to_dict(profile_data) if profile_data else None,
            "general_data": object_to_dict(general_data) if general_data else None,
            "drilling_parameters": (
                object_to_dict(drilling_parameter_data)
                if drilling_parameter_data
                else None
            ),
            "afe": object_to_dict(afe_data) if afe_data else None,
            "personnel_in_charge": (
                object_to_dict(personnel_data) if personnel_data else None
            ),
            "summary": object_to_dict(summary_data) if summary_data else None,
            "time_breakdown": (
                [object_to_dict(tb) for tb in time_breakdown_data]
                if time_breakdown_data
                else None
            ),
        }

        return jsonify(report_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
