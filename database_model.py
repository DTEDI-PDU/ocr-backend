from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy instance (no Flask app here)
db = SQLAlchemy()

# Define your database model
class WellReport(db.Model):
    __tablename__ = 'well_report'  # Optional: specify table name

    id = db.Column(db.Integer, primary_key=True)
    operator = db.Column(db.String(100))
    contractor = db.Column(db.String(100))
    report_no = db.Column(db.String(50))
    well_pad_name = db.Column(db.String(100))
    field = db.Column(db.String(50))
    well_type_profile = db.Column(db.String(100))
    latitude_longitude = db.Column(db.String(100))
    environment = db.Column(db.String(50))
    gl_msl_m = db.Column(db.Float)

    # Constructor
    def __init__(self, operator, contractor, report_no, well_pad_name, field,
                 well_type_profile, latitude_longitude, environment, gl_msl_m):
        self.operator = operator
        self.contractor = contractor
        self.report_no = report_no
        self.well_pad_name = well_pad_name
        self.field = field
        self.well_type_profile = well_type_profile
        self.latitude_longitude = latitude_longitude
        self.environment = environment
        self.gl_msl_m = gl_msl_m

    # Optional: String representation of the object for debugging
    def __repr__(self):
        return f"<WellReport {self.report_no} - {self.well_pad_name}>"
