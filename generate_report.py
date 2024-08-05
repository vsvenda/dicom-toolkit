import os
import pandas as pd
import pydicom
from datetime import datetime
from dateutil import parser

def read_excel(file_path):
    # Load the Excel file
    df = pd.read_excel(file_path, dtype={'JMBG': str})
    # Convert 'Vreme kreiranja' to datetime
    df['Vreme kreiranja'] = pd.to_datetime(df['Vreme kreiranja'], errors='coerce')
    return df

def find_closest_date(target, dates):
    # Filter dates to only include those on or before the target date
    valid_dates = [date for date in dates if date <= target]
    # Find the closest date that is on or before the target date
    if valid_dates:
        return min(valid_dates, key=lambda d: abs(d - target))
    else:
        return None  # Return None if no valid date found

def process_dicom_files(directory, info_df):
    results = []
    # Traverse the directory containing subfolders for each patient
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                # Read DICOM file
                ds = pydicom.dcmread(filepath, stop_before_pixels=True)
                study_date = datetime.strptime(ds.StudyDate, '%Y%m%d').date()
                patient_id = os.path.basename(root)
                image_id = file

                # Filter info_df for current patient_id
                patient_info = info_df[info_df['JMBG'] == patient_id]
                # Make sure 'Vreme kreiranja' is treated as date only for comparison
                patient_info['Vreme kreiranja'] = patient_info['Vreme kreiranja'].dt.date

                # Get the closest screening date from the patient-specific data
                closest_date = find_closest_date(study_date, patient_info['Vreme kreiranja'])
                if closest_date:
                    closest_row = patient_info[patient_info['Vreme kreiranja'] == closest_date]

                    # Assume images are named or tagged with L or R for left/right breast
                    if 'L' in file.upper():
                        birads = closest_row['BIRADS L'].values[0]
                    elif 'R' in file.upper():
                        birads = closest_row['BIRADS D'].values[0]
                    else:
                        birads = 'Unknown'

                    results.append([patient_id, image_id, closest_date.strftime('%Y-%m-%d'), birads])
                else:
                    print(f"No valid screening date found for {filepath}")
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    return results

def main():
    info_path = 'path_to_info.xls'
    dicom_directory = 'path_to_dicom_directory'
    output_path = 'output.csv'

    # Load and process the Excel data
    info_df = read_excel(info_path)

    # Process each DICOM file and gather results
    result_data = process_dicom_files(dicom_directory, info_df)

    # Create DataFrame and save to CSV
    columns = ['PatientID', 'ImageID', 'Date', 'BIRADS']
    result_df = pd.DataFrame(result_data, columns=columns)
    result_df.to_csv(output_path, index=False)
    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    main()
