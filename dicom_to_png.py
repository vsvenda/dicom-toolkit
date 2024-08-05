import os
import sys
import pydicom
import numpy as np
import cv2
from minio import Minio
from minio.error import S3Error
import re
import psycopg2
from psycopg2 import sql
from utils import load_env


def get_attr(dicom, attr, default=' '):
    """ Retrieve an attribute from a DICOM image with a default if not present.
        Convert to string as database expects 'text'
    """
    value = getattr(dicom, attr, default)
    return str(value) if value != default else default


# Function to insert data into dicom_metadata table
def insert_dicom_metadata(table_name, mammography_id, patient_name, patient_id, acquisition_date, acquisition_time,
                          view, laterality, implant, manufacturer, manufacturer_model, institution):
    """ Extract dicom metadata and store to postgres database table """
    conn = None
    cursor = None

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

        # Check if the study_id already exists
        cursor.execute(sql.SQL("SELECT EXISTS(SELECT 1 FROM {table} WHERE mammography_id = %s)").format(
            table=sql.Identifier(table_name)), (mammography_id,))
        exists = cursor.fetchone()[0]

        if exists:
            print(f"mammography_id {mammography_id} already exists in the table {table_name}. No data inserted.")
        else:
            # Define the insert statement
            insert_query = sql.SQL("""
                INSERT INTO {table} (mammography_id, patient_name, patient_id, acquisition_date, acquisition_time,
                          view, laterality, implant, manufacturer, manufacturer_model, institution)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """).format(table=sql.Identifier(table_name))

            # Execute the insert statement
            cursor.execute(insert_query, (mammography_id, patient_name, patient_id, acquisition_date, acquisition_time,
                                          view, laterality, implant, manufacturer, manufacturer_model, institution))

            # Commit the transaction
            conn.commit()

            print(f"Data for mammography_id {mammography_id} successfully inserted into {table_name}.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def png_to_minio(dicom_folder):
    """ Load dicom image, convert to .png format and store in minio server (if it is not already there)
        Once the image is processed, add corresponding metadata to the sql table (using insert_dicom_metadata function)
    :param dicom_folder: path to dicom folder
    """

    minio_host = load_env('MINIO_HOST')
    minio_acc_key = load_env('MINIO_ACC_KEY')
    minio_secret_key = load_env('MINIO_SECRET_KEY')

    for filename in os.listdir(dicom_folder):
        dicom_path = os.path.join(dicom_folder, filename)
        dicom_image = pydicom.dcmread(dicom_path)
        # Get the pixel array from the DICOM file
        pixel_array = dicom_image.pixel_array
        # Normalize the pixel values to be in the range 0-255 (for 8-bit greyscale)
        pixel_array = ((pixel_array - np.min(pixel_array)) / (np.max(pixel_array) - np.min(pixel_array))) * 255.0
        pixel_array = pixel_array.astype(np.uint8)
        # Define path for .png image
        png_image = os.path.basename(dicom_path)
        png_image = re.sub(r'\.(dcm|dicom)$', '', png_image)
        png_image = png_image + '.png'  # image name
        png_filepath = os.path.join(os.getcwd(), png_image)  # image path
        # Save .png image locally
        cv2.imwrite(png_filepath, pixel_array)

        # Save to minio
        client = Minio(minio_host,
                       access_key=minio_acc_key,
                       secret_key=minio_secret_key,
                       secure=False
                       )
        try:  # Check if .png file has already been uploaded
            # Try to get the object's metadata
            client.stat_object("firstbucket", png_image)
            print(f"Object '{png_image}' already exists in firstbucket. Skipping upload.")
        except S3Error as e:
            # If the object does not exist, an exception is thrown
            if e.code == 'NoSuchKey':
                # Object does not exist, proceed with upload
                try:
                    result = client.fput_object("firstbucket", png_image, png_filepath)
                    print(f"Uploaded object {png_image}, etag: {result.etag}")
                except S3Error as err:
                    print(f"Failed to upload object {png_image} due to: {err}")
            else:
                # Other S3 errors
                print(f"Error occurred: {e}")

        # Remove the locally saved .png image
        os.remove(png_filepath)

        # Add metadata info to table. Not all dicom have all the data (default = ' ')

        dcm_study_id = re.sub(r'\.(dcm|dicom)$', '', os.path.basename(dicom_path))
        # Name of postgres table for dicom metadata
        table_name = 'dicom_metadata'
        insert_dicom_metadata(
            table_name,
            dcm_study_id,
            get_attr(dicom_image, 'PatientName'),
            get_attr(dicom_image, 'PatientID'),
            get_attr(dicom_image, 'AcquisitionDate'),
            get_attr(dicom_image, 'AcquisitionTime'),
            get_attr(dicom_image, 'ViewPosition'),  # Could be missing
            get_attr(dicom_image, 'ImageLaterality'),  # Could be missing
            get_attr(dicom_image, 'BreastImplantPresent'),  # Custom default value
            get_attr(dicom_image, 'Manufacturer'),
            get_attr(dicom_image, 'ManufacturerModelName'),
            get_attr(dicom_image, 'InstitutionName')
        )


if __name__ == '__main__':
    if len(sys.argv) > 1:
        png_to_minio(sys.argv[1])
    else:
        print("Please provide dicom folder path.")
