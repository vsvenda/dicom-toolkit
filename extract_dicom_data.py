import os
import csv
import pydicom
import pandas as pd


def read_birads_data(birads_xls):
    # Create a dictionary to map PatientID to (BIRADS L, BIRADS D)
    df = pd.read_excel(birads_xls, dtype={'JMBG': str})
    birads_map = {row['JMBG']: (row.get('BIRADS L').strip(), row.get('BIRADS D').strip()) for index, row in df.iterrows()}
    return birads_map


def extract_dicom_data(directory_path, birads_map, output_csv):
    fields = ['PatientID', 'ImageLaterality', 'ViewPosition']
    dicom_data_list = []

    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            try:
                dicom_data = pydicom.dcmread(file_path)
                row = [getattr(dicom_data, field, 'N/A') for field in fields]
                row.insert(1, file_name)  # Insert ImageID

                # Determine the appropriate BIRADS value based on laterality
                birads_pair = birads_map[row[0]]
                birads_value = birads_pair[0] if row[2] == 'L' else birads_pair[1]
                row.append(birads_value)

                dicom_data_list.append(row)
                print(f"Added info for {file_name}")
            except Exception as e:
                print(f"Failed to process {file_name}: {e}")

    dicom_data_list.sort(key=lambda x: x[0])
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['PatientID', 'ImageID', 'Laterality', 'ViewPosition', 'BIRADS'])
        writer.writerows(dicom_data_list)


# Usage
birads_csv = '...'  # Path to the BIRADS classification CSV
directory_path = '...'  # DICOM files directory
output_csv = '...'  # Output CSV file path
birads_map = read_birads_data(birads_csv)
extract_dicom_data(directory_path, birads_map, output_csv)
