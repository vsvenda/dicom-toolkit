import subprocess
import sys
from utils import load_env


def dwnld(initial_date, end_date):
    """Download all dicom MG images in the time span of initial_date - end_date"""
    current_date = initial_date

    # Retrieve PACS information from environment variables (IP, port, and AE title of the remote PACS server)
    pacs_ip = load_env('PACS_IP')
    pacs_port = load_env('PACS_PORT')
    pacs_ae_title = load_env('PACS_AE_TITLE')

    while current_date != end_date+1:
        # Define the command and parameters as a list
        command = [
            'movescu',
            '-aet', 'PYNETDICOM',
            '-aec', pacs_ae_title,
            pacs_ip, pacs_port,
            '-k', '0008,0052=SERIES',
            '-k', '0008,0016=1.2.840.10008.5.1.4.1.1.1.2',
            '-k', '0008,0020='+str(current_date),
            '-d'
        ]

        # Execute the command
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            current_date += 1
        except subprocess.CalledProcessError as e:
            print("Error occurred:", e)
            print("Error output:", e.stderr)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        dwnld(sys.argv[1], sys.argv[2])
    else:
        print("Please provide initial and end date for dicom of interest.")
