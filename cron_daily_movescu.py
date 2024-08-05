import subprocess
import sys
from datetime import datetime
from utils import load_env


def dwnld():
    """Download DICOM images for the current date and log output to a .txt file."""
    # Format the current datetime to include in the file name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'download_{timestamp}.txt'
    sys.stdout = open(output_file, 'w')  # Redirect all prints to this file

    dicom_date = datetime.now().strftime('%Y%m%d')  # Only the current date

    # Retrieve PACS information from environment variables (IP, port, and AE title of the remote PACS server)
    pacs_ip = load_env('PACS_IP')
    pacs_port = load_env('PACS_PORT')
    pacs_ae_title = load_env('PACS_AE_TITLE')

    command = [
        'movescu',
        '-aet', 'PYNETDICOM',
        '-aec', pacs_ae_title,
        pacs_ip, pacs_port,
        '-k', '0008,0052=SERIES',
        '-k', '0008,0016=1.2.840.10008.5.1.4.1.1.1.2',
        '-k', '0008,0020=' + dicom_date,
        '-d'
    ]

    # Execute the command
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Downloaded images for {dicom_date}")
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e)
        print("Error output:", e.stderr)

    sys.stdout.close()  # Close the file and restore stdout to default
    sys.stdout = sys.__stdout__


if __name__ == '__main__':
    dwnld()  # Download for the current date
