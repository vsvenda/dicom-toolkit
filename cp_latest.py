import os
import shutil
import pydicom
import sys


def copy_latest_dicom(source_folder, destination_folder, laterality):
    """
    Filters DICOM files for a specified Laterality, sorts them by StudyDate, and copies all images from the latest date.

    Parameters:
    - source_folder: The directory containing the original DICOM files.
    - destination_folder: The directory where the filtered files will be copied.
    - laterality: The Laterality to filter on ('L' or 'R').
    """
    dicom_files = []

    # Read all DICOM files, filter by Laterality, and sort by StudyDate
    for file_name in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file_name)
        try:
            dicom_data = pydicom.dcmread(file_path)
            if dicom_data.get('ImageLaterality', '').upper() == laterality.upper():
                dicom_files.append(dicom_data)
        except Exception as e:
            print(f"Skipping {file_name}: {e}")

    if not dicom_files:
        print(f"Laterality {laterality}: No matching files found.")
        return

    # Sort the files by StudyDate in descending order
    dicom_files.sort(key=lambda x: x.StudyDate, reverse=True)

    # Determine the latest date
    latest_date = dicom_files[0].StudyDate
    print(f"Laterality {laterality}: Latest date: {latest_date}")

    # Filter files to include only those from the latest date
    latest_files = [df for df in dicom_files if df.StudyDate == latest_date]

    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Copy the latest DICOM files from the latest date
    for dicom_data in latest_files:
        file_path = dicom_data.filename
        shutil.copy(file_path, os.path.join(destination_folder, os.path.basename(file_path)))
        print(f"Laterality {laterality}: Copied {os.path.basename(file_path)} to {destination_folder}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 script_name.py <source_folder> <destination_folder> <laterality>")
        sys.exit(1)

    source = sys.argv[1]
    destination = sys.argv[2]
    laterality = sys.argv[3]

    copy_latest_dicom(source, destination, laterality)
