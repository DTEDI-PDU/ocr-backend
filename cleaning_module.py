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
