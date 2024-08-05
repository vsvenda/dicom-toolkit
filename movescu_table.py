import pandas as pd
import subprocess
from datetime import datetime, timedelta
from utils import load_env
from cp_latest import copy_latest_dicom
import sys
import os


# Define a function to execute the movescu command
def execute_movescu(patiendID, date, pacs_ae_title, pacs_ip, pacs_port):
    """Download patient dicom MG images based on patientID (jmbg) and report date (Vreme kreiranja)"""
    try:
        # Set beginning (3 months ago) and end (1 day ahead) dates
        date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        beginning_date = date_obj - timedelta(days=90)
        beginning_date = beginning_date.strftime('%Y%m%d'),
        end_date = date_obj + timedelta(days=1)
        end_date = end_date.strftime('%Y%m%d')

        print(f"Beginning date {beginning_date}")
        print(f"End date {end_date}")

        command = [
            'movescu', '-aet', 'PYNETDICOM', '-aec', pacs_ae_title, pacs_ip, pacs_port,
            '-k', '0008,0052=SERIES',
            '-k', '0008,0016=1.2.840.10008.5.1.4.1.1.1.2',
            '-k', f'0008,0020={beginning_date}-{end_date}',
            '-k', f'0010,0020={patiendID}',
            '-d'
        ]
        print(command)
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"Images copied for patient {patiendID}")

    except subprocess.CalledProcessError as e:
        print("An error occurred while executing movescu:", e.stderr.decode())
    except Exception as e:
        print("An unexpected error occurred:", str(e))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("Usage: python3 movescu_table.py <excel_table_path>")
        sys.exit(1)

    # Create log file and redirect print statements to it
    log_filename = 'movescu_table.txt'
    f = open(log_filename, 'w', encoding='utf-8')
    sys.stdout = f

    data = pd.read_excel(sys.argv[1], dtype={'JMBG': str})  # patient data

    # Retrieve PACS information from environment variables (IP, port, and AE title of the remote PACS server)
    pacs_ip = load_env('PACS_IP')
    pacs_port = load_env('PACS_PORT')
    pacs_ae_title = load_env('PACS_AE_TITLE')

    # Count the number of positive/negative birads
    birads_pos = 0
    birads_neg = 0

    # Iterate through each row (process one patient at a time)
    for index, row in data.iterrows():
        # Extract needed patient info (update column names based on your table)
        patient_id = row['JMBG']
        date = row['Vreme kreiranja']

        print(f"\nWorking on patient {patient_id}")

        birads_l = str(row['BIRADS L']).strip()
        birads_r = str(row['BIRADS D']).strip()

        if birads_l in ['2', '4', '4a', '4b', '4c', '5', '6'] or birads_r in ['2', '4', '4a', '4b', '4c', '5', '6']:
            if birads_l in ['4', '4a', '4b', '4c', '5', '6'] or birads_r in ['4', '4a', '4b', '4c', '5', '6'] or birads_neg < birads_pos + 10:
                # download dicom
                execute_movescu(patient_id, date, pacs_ae_title, pacs_ip, pacs_port)

                if birads_l == '2':
                    birads_neg += 1
                elif birads_l in ['4', '4a', '4b', '4c', '5', '6']:
                    birads_pos += 1
                if birads_r == '2':
                    birads_neg += 1
                elif birads_r in ['4', '4a', '4b', '4c', '5', '6']:
                    birads_pos += 1
                print(f"Number of occurrences with negative birads: {birads_neg}")
                print(f"Number of occurrences with positive birads: {birads_pos}")

