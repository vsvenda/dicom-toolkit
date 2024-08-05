import os
import sys
import zlib
from cryptography.fernet import Fernet
import pydicom


def encrypt_data(data, key):
    """Encrypt and compress data using the provided key."""
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data.encode())
    compressed_data = zlib.compress(encrypted_data)
    return compressed_data


def encrypt(folder_path):
    """Encrypt PatientName and PatientID in all dicom files in folder_path."""
    key = os.getenv('AES_KEY')  # load AES key
    if not key:
        raise EnvironmentError("AES_KEY environment variable not set.")

    for entry in os.listdir(folder_path):
        dicom_path = os.path.join(folder_path, entry)
        if os.path.isfile(dicom_path):
            try:
                ds = pydicom.dcmread(dicom_path)
                if hasattr(ds, 'PatientName'):
                    ds.add_new((0x1001, 0x0010), 'OB', encrypt_data(ds.PatientName, key))  # patient name
                    ds.PatientName = 'anonymized data'
                if hasattr(ds, 'PatientID'):
                    ds.add_new((0x1001, 0x0020), 'OB', encrypt_data(ds.PatientID, key))  # patient ID
                    ds.PatientID = 'anonymized data'
                ds.save_as(dicom_path)
                print(f"Encrypted {dicom_path}")
            except Exception as e:
                print(f"Failed to process {dicom_path}: {str(e)}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        encrypt(sys.argv[1])
    else:
        print("Please provide dicom folder.")
