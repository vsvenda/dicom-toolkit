# PROJECT OVERVIEW
This collection of scripts provides a comprehensive suite of tools designed to automate and facilitate various tasks
related to DICOM image processing, PACS communication, data security, and environment configuration in medical imaging.
Each script addresses specific requirements ranging from downloading and processing DICOM files, matching imaging data
with diagnostic information, securely handling sensitive data, and validating operational configurations.

Make sure to set all necessary environment variables for pacs operations
export PACS_IP='...'
export PACS_PORT='...'
export PACS_AE_TITLE='...'

Make sure to set all necessary environment variables for encryption/decryption
export AES_KEY='...'

Make sure to set all necessary environment variables for minio server connection
export MINIO_HOST='...'
export MINIO_ACC_KEY='...'
export MINIO_SECRET_KEY='...'


# cp_latest.py
This script is designed to process DICOM files based on their laterality attribute ('L' for left or 'R' for right).
It filters, sorts, and copies DICOM images from the most recent study date within a specified source directory to a
designated destination directory.

Usage: python3 copy_latest_dicom.py <source_folder> <destination_folder> <laterality>
<source_folder>: The path to the directory containing the DICOM files.
<destination_folder>: The path to the directory where the filtered files should be copied.
<laterality>: Specifies the laterality to filter the DICOM files ('L' for left or 'R' for right).


# cron_daily_movescu.py
This script automates the downloading of DICOM images from a PACS server based on the current date.
It also logs the process to a text file named with a timestamp to facilitate tracking and debugging.

Usage: python3 download_dicom.py


# cron_new_dicom.py
This script coordinates the retrieval and synchronization of DICOM metadata between a PACS system and a PostgreSQL database,
specifically focusing on data from the last week. It ensures that all relevant DICOM metadata extracted from PACS is
also present in the database and initiates downloads of any missing images.

Usage: python3 cron_new_dicom.py


# decrypt.py
This script is designed to decrypt and decompress sensitive data (PatientName and PatientID) embedded in DICOM files
within a specified directory. The encryption key is expected to be stored as an environment variable.

Usage: python3 decrypt_dicom.py <folder_path>
<folder_path>: The path to the directory containing the DICOM files to be decrypted.


# dicom_to_png.py
This script is designed to process DICOM files by converting them to PNG format and uploading the resulting images to a
Minio server (an S3-compatible object storage system). Additionally, it extracts metadata from the DICOM files and
inserts it into a PostgreSQL database.

Usage: python3 convert_and_store_png.py <dicom_folder_path>
<dicom_folder_path>: The path to the directory containing the DICOM files to be processed.


# encrypt.py
This script is designed to compress and encrypt sensitive data (PatientName and PatientID) embedded in DICOM files
within a specified directory. The encryption key is expected to be stored as an environment variable.

Usage: python3 encrypt_dicom.py <folder_path>
<folder_path>: The path to the directory containing the DICOM files to be encrypted.


# extract_dicom_data.py
This script automates the process of extracting key metadata from DICOM files and annotating these with BIRADS
classification information from an Excel spreadsheet. The final output is a CSV file containing consolidated data that
includes patient identifiers, image IDs, and corresponding BIRADS scores.

Usage: Set birads_xls to the path of the Excel file containing BIRADS data.
Set directory_path to the directory containing DICOM files.
Set output_csv to the desired path for the output CSV file.
python3 extract_dicom_data.py


# findscu.py
This script facilitates the retrieval of patient and imaging data from a PACS server using the C-FIND operation
defined in the DICOM standards. It is specifically configured to fetch mammography series over a defined date range.

Usage: Modify the Identifier (query) dataset with the data you want to request.
python3 findscu.py


# generate_key.py
 This simple script generates a secure encryption key using the Fernet symmetric encryption scheme from the
 cryptography library. The key is essential for encrypting and decrypting sensitive data securely.

Usage: python3 generate_encryption_key.py


# generate_report.py
This script integrates DICOM image metadata with BIRADS ratings from an Excel file, focusing on matching each DICOM file
with the closest screening date and its corresponding BIRADS assessment. It processes DICOM files from a directory
structure where each patient's images are stored in separate subfolders named after their unique identifier.

Usage: Set info_path to the Excel file containing patient screening information.
Set dicom_directory to the root directory containing subfolders for each patient's DICOM files.
Set output_path to the desired file path for the resulting CSV.
python3 generate_report.py


# movescu.sh
This Bash script iteratively queries a PACS server for DICOM series using specific date parameters, utilizing the
movescu command from the DICOM toolkit. It is designed to perform daily queries over a specified date range to retrieve
medical imaging data.

Usage: Modify the initial_date and end_date variables as needed for the desired query period.
chmod +x movescu.sh  
./movescu.sh 


# movescu_dates.py
 This Python script facilitates the downloading of DICOM mammography (MG) images over a specified date range from a
 PACS server. It utilizes the movescu tool to perform series-level DICOM queries and retrievals based on date criteria.

Usage: python download_dicom_series.py <start_date> <end_date>
<start_date>: Initial date for image downloading.
<end_date>: End date for image downloading.


# movescu_table.py
This Python script is designed to automate the retrieval of DICOM mammography images based on patient information from
an Excel file. Additionally, the script handles BIRADS classifications to selectively retrieve and process images
associated with certain BIRADS scores.

Usage: python3 movescu_table.py <path_to_excel_file> 
<path_to_excel_file> Excel file from which to extract image info.


# utils.py
This Python utility script is designed to safely load and validate environment variables required for various operations,
specifically ensuring the environment variables are set and correctly formatted before proceeding with operations that
depend on these settings. The function load_env(env_name) can be called with the name of the environment variable as an
argument to retrieve and validate its value. Common use cases include loading configuration for database connections or
external service integrations, where proper settings are critical for operation.

Usage: # Example of how to use the function
pacs_port = load_env('PACS_PORT')
 

