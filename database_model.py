from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy instance (no Flask app here)
db = SQLAlchemy()

# Define your database model
class Profile(db.Model):
    ___tablename__ = 'profile'  # Optional: specify table name

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

# GeneralData Model
class GeneralData(db.Model):
    __tablename__ = 'general_data'
    id = db.Column(db.Integer, primary_key=True)
    rig_type_name = db.Column(db.String(255), nullable=True)
    rig_power = db.Column(db.String(255), nullable=True)
    kb_elevation = db.Column(db.String(255), nullable=True)
    midnight_depth = db.Column(db.String(255), nullable=True)
    progress = db.Column(db.String(255), nullable=True)
    proposed_td = db.Column(db.String(255), nullable=True)
    spud_date = db.Column(db.String(255), nullable=True)
    release_date = db.Column(db.String(255), nullable=True)
    planned_days = db.Column(db.String(255), nullable=True)
    days_from_rig_release = db.Column(db.String(255), nullable=True)

# DrillingParameter Model
class DrillingParameter(db.Model):
    __tablename__ = 'drilling_parameters'
    id = db.Column(db.Integer, primary_key=True)
    average_wob_24_hrs = db.Column(db.String(255), nullable=True)
    average_rop_24_hrs = db.Column(db.String(255), nullable=True)
    average_surface_rpm_dhm = db.Column(db.String(255), nullable=True)
    on_off_bottom_torque = db.Column(db.String(255), nullable=True)
    flowrate_spp = db.Column(db.String(255), nullable=True)
    air_rate = db.Column(db.String(255), nullable=True)
    corr_inhib_foam_rate = db.Column(db.String(255), nullable=True)
    puw_sow_rotw = db.Column(db.String(255), nullable=True)
    total_drilling_time = db.Column(db.String(255), nullable=True)
    ton_miles = db.Column(db.String(255), nullable=True)

    # Initialize the database in your app
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()