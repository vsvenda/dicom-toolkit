#!/bin/bash

# Define initial and end dates in YYYYMMDD format
initial_date="20200101"
end_date="20203103"

# Convert dates to seconds since the epoch
current_date=$(date -d $initial_date +%s)
end_date=$(date -d $end_date +%s)


# Ensure that all required environment variables are set
if [ -z "$PACS_AE_TITLE" ] || [ -z "$PACS_IP" ] || [ -z "$PACS_PORT" ]; then
  echo "Error: One or more environment variables are not set."
  echo "Ensure that AE_TITLE, IP_ADDRESS, and PORT are exported."
  exit 1
fi

# Loop through dates
while [ $current_date -le $end_date ]
do
  # Format current date back to YYYYMMDD for the DICOM tag
  formatted_date=$(date -d @$current_date +%Y%m%d)

  # Define the command and parameters (replace dummy values with your actual parameters)
  movescu -aet PYNETDICOM -aec $PACS_AE_TITLE $PACS_IP $PACS_PORT -k 0008,0052=SERIES -k 0008,0016=1.2.840.10008.5.1.4.1.1.1.2 -k 0008,0020=$formatted_date -d

  # Check for command success
  if [ $? -eq 0 ]; then
    echo "Command succeeded for date $formatted_date"
  else
    echo "Command failed for date $formatted_date"
  fi

  # Increment date by one day (86400 seconds)
  current_date=$(($current_date + 86400))
done