from pynetdicom import AE
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind
from pydicom.dataset import Dataset
import psycopg2
from psycopg2 import sql
from datetime import datetime
from dateutil.relativedelta import relativedelta
import subprocess
from utils import load_env


def cfind(start_date, end_date):
    """ Retrieve DICOM metadata from PACS using c-find for a specified date range """
    # Initialize the Application Entity
    ae = AE()

    # Add a requested presentation context
    ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)

    # Create our Identifier (query) dataset
    ds = Dataset()
    ds.PatientName = '*'
    ds.PatientID = '*'
    ds.StudyDate = f"{start_date}-{end_date}"
    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.1.2'  # DigitalMammographyXRayImageStorageForPresentation
    ds.QueryRetrieveLevel = 'IMAGE'  # Could be STUDY, SERIES, or IMAGE

    # Retrieve PACS information from environment variables (IP, port, and AE title of the remote PACS server)
    pacs_ip = load_env('PACS_IP')
    pacs_port = load_env('PACS_PORT')
    pacs_ae_title = load_env('PACS_AE_TITLE')

    # Send the C-FIND request
    assoc = ae.associate(pacs_ip, pacs_port, ae_title=pacs_ae_title)
    images_info = []

    if assoc.is_established:
        responses = assoc.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind)
        for (status, identifier) in responses:
            if status and status.Status in (0xFF00, 0xFF01):  # Pending responses
                row = (
                    identifier.get('PatientName', ''),
                    identifier.get('PatientID', ''),
                    identifier.get('StudyDate', '')
                )
                images_info.append(row)

        assoc.release()
    else:
        print('Association rejected, aborted or never connected')

    # Count occurrences and keep unique
    row_count = {}
    for row in images_info:
        if row in row_count:
            row_count[row] += 1
        else:
            row_count[row] = 1
    # Convert to list including counts
    unique_images_info = [[*row, count] for row, count in row_count.items()]

    return unique_images_info


def read_postgres(table_name, start_date, end_date):
    """ Retrieve DICOM metadata from a postgres database table for a specified date range """
    conn = None
    cursor = None
    records = []

    # Retrieve database information from environment variables (name, user, pass, host, port)
    db_name = load_env('DB_NAME')
    db_user = load_env('DB_USER')
    db_pass = load_env('DB_PASS')
    db_host = load_env('DB_HOST')
    db_port = load_env('DB_PORT')

    # Database connection parameters
    db_params = {
        'dbname': db_name,
        'user': db_user,
        'password': db_pass,
        'host': db_host,
        'port': db_port
    }

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Define the select statement to filter by date range
        select_query = sql.SQL("""
                    SELECT patient_name, patient_id, acquisition_date, COUNT(*)
                    FROM {table}
                    WHERE acquisition_date BETWEEN %s AND %s
                    GROUP BY patient_name, patient_id, acquisition_date
                    ORDER BY acquisition_date, patient_name
                """).format(table=sql.Identifier(table_name))

        # Execute the select statement
        cursor.execute(select_query, (start_date, end_date))

        # Fetch all the rows
        records = cursor.fetchall()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return records


def compare_results(cfind_results, postgres_results):
    """ Compare results from PACS and postgres and return whatever exists in PACS but not in postgres """
    # Ensure that all data types are consistent (e.g., converting all to strings for direct comparison)
    cfind_set = set(tuple(str(x) for x in row) for row in cfind_results)
    postgres_set = set(tuple(str(x) for x in row) for row in postgres_results)

    # Find elements in cfind set not in postgres set
    unique_to_cfind = cfind_set - postgres_set
    return unique_to_cfind


def cmove(entries):
    """ Download DICOM images """

    # Retrieve PACS information from environment variables (IP, port, and AE title of the remote PACS server)
    pacs_ip = load_env('PACS_IP')
    pacs_port = load_env('PACS_PORT')
    pacs_ae_title = load_env('PACS_AE_TITLE')

    for entry in unique_entries:
        patient_name, patient_id, study_date, num_images = entry
        command = [
            'movescu', '-aet', 'PYNETDICOM', '-aec', pacs_ae_title, pacs_ip, pacs_port,
            '-k', '0008,0052=IMAGE',
            '-k', '0008,0016=1.2.840.10008.5.1.4.1.1.1.2',  # SOP Class UID for Digital Mammography X-Ray
            '-k', f'0008,0020={study_date}',
            '-k', f'0010,0020={patient_id}',
            '-d'
        ]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            print(f'Success running movescu for {patient_id}, {study_date}: {result.stdout.decode()}')
        except subprocess.CalledProcessError as e:
            print(f'Error running movescu for {patient_id}, {study_date}: {e.stderr.decode()}')

if __name__ == '__main__':
    # Name of postgres table for dicom metadata
    table_name = 'dicom_metadata'
    # Start and end date
    end_date = datetime.now()  # Current date
    start_date = end_date - relativedelta(days=6)  # How far back we want to go for data extraction (days, months, years)

    # Format dates for the queries
    formatted_end_date = end_date.strftime('%Y%m%d')
    formatted_start_date = start_date.strftime('%Y%m%d')
    print(f"Start date: {formatted_start_date}")
    print(f"End date: {formatted_end_date}")

    # C-find dicom images in pacs
    cfind_data = cfind(formatted_start_date, formatted_end_date)
    print(f"\nThe following data was extracted using c-find:\n{cfind_data}")

    # Existing dicom images in postgres
    postgres_data = read_postgres(table_name, formatted_start_date, formatted_end_date)
    print(f"\nThe following data was extracted from postgres:\n{postgres_data}")

    # Check what is missing in postgres
    unique_entries = compare_results(cfind_data, postgres_data)
    print(f"\nThe following is the difference between c-find and postgres:\n{unique_entries}")

    cmove(unique_entries)







