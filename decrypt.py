import os
import sys
import zlib
from cryptography.fernet import Fernet
import pydicom


def decrypt_decompress_data(data, key):
    """Decrypt and decompress data using the provided key."""
    cipher_suite = Fernet(key)
    decompressed_data = zlib.decompress(data)
    decrypted_data = cipher_suite.decrypt(decompressed_data)
    return decrypted_data.decode()


def decrypt(folder_path):
    """Decrypt PatientName and PatientID in all dicom files in folder_path."""
    key = os.getenv('AES_KEY')  # load AES key
    if not key:
        raise EnvironmentError("AES_KEY environment variable not set.")

    for entry in os.listdir(folder_path):
        dicom_path = os.path.join(folder_path, entry)
        if os.path.isfile(dicom_path):
            try:
                ds = pydicom.dcmread(dicom_path)
                if (0x1001, 0x0010) in ds:
                    ds.PatientName = decrypt_decompress_data(ds[0x1001, 0x0010].value, key)     # patient name
                if (0x1001, 0x0020) in ds:
                    ds.PatientID = decrypt_decompress_data(ds[0x1001, 0x0020].value, key)       # patient ID
                ds.save_as(dicom_path)
                print(f"Decrypted {dicom_path}")
            except Exception as e:
                print(f"Failed to process {dicom_path}: {str(e)}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        decrypt(sys.argv[1])
    else:
        print("Please provide dicom folder.")
