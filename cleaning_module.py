import re

def cleaning_profile(df):
    # Extract the rows you want to process (in this case rows 1 to 4, column 0)
    extracted_data = df.iloc[1:4, 0].values

    # Define regex patterns for each field
    patterns = {
        'operator': r'OPERATOR\s+(.*)\s+CONTRACTOR',
        'contractor': r'CONTRACTOR\s+(.*)\s+REPORT NO',
        'report_no': r'REPORT NO.\s+#\s*(\d+)',
        'well_pad_name': r'WELL/\s*PAD NAME\s+(.*?)\s+FIELD',
        'field': r'FIELD\s+(\w+)',
        'well_type_profile': r'WELL\s*TYPE/\s*PROFILE\s+(.*?)\s+LATITUDE',
        'latitude_longitude': r'LATITUDE/\s*LONGITUDE\s+(.*?)\s+GL',
        'environment': r'ENVIRONTMENT\s+(\w+)',
        'gl_msl_m': r'GL\s+-\s+MSL\s*\(M\)\s*(.*)',
    }

    profile_data = {}

    # Loop through each pattern and try to find a match in the extracted data
    for key, pattern in patterns.items():
        for line in extracted_data:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                profile_data[key] = match.group(1).strip()
                break

    return profile_data

def cleaning_general(df):
    start_index = df[df.apply(lambda x: x.astype(str).str.contains('GENERAL').any(), axis=1)].index[0]
    end_index = df[df.apply(lambda x: x.astype(str).str.contains('24 HOURS SUMMARY').any(), axis=1)].index[0]
    df_cleaned = df.iloc[start_index + 1:end_index - 1, 4].reset_index(drop=True)

    patterns = [
        'rig_type_name',
        'rig_power',
        'kb_elevation',
        'midnight_depth',
        'progress',
        'proposed_td',
        'spud_date',
        'release_date',
        'planned_days',
        'days_from_rig_release'
    ]

    result_dict = {patterns[i]: df_cleaned[i] for i in range(len(patterns))}

    return result_dict

def cleaning_drilling_parameter(df):
    start_index = df[df.apply(lambda x: x.astype(str).str.contains('DRILLING PARAMETERS').any(), axis=1)].index[0]
    end_index = df[df.apply(lambda x: x.astype(str).str.contains('24 HOURS SUMMARY').any(), axis=1)].index[0]
    df_cleaned = df.iloc[start_index + 1:end_index - 1, 11].reset_index(drop=True)

    patterns = [
        'average_wob_24_hrs',
        'average_rop_24_hrs',
        'average_surface_rpm_dhm',
        'on_off_bottom_torque',
        'flowrate_spp',
        'air_rate',
        'corr_inhib_foam_rate',
        'puw_sow_rotw',
        'total_drilling_time',
        'ton_miles'
    ]

    result_dict = {patterns[i]: df_cleaned[i] for i in range(len(patterns))}

    return result_dict