from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind
from pydicom.dataset import Dataset
from utils import load_env


# Uses pynetdicom findscu (c-find) functionality to retrieve patient info from pacs

# Initialize the Application Entity
debug_logger()
ae = AE()

# Add a requested presentation context
ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)

# Create our Identifier (query) dataset
# modify PatientName, PatientID, StudyDate, etc., with your requirements
ds = Dataset()
ds.PatientName = '*'
ds.PatientID = '*'
ds.StudyDate = '20220420-20220922'
ds.Modality = 'MG'  # MG is the DICOM modality code for mammography
ds.QueryRetrieveLevel = 'SERIES'  # Could be STUDY, SERIES, or IMAGE

# Retrieve PACS information from environment variables (IP, port, and AE title of the remote PACS server)
pacs_ip = load_env('PACS_IP')
pacs_port = load_env('PACS_PORT')
pacs_ae_title = load_env('PACS_AE_TITLE')

# Send the C-FIND request
assoc = ae.associate(pacs_ip, pacs_port, ae_title=pacs_ae_title)
cnt = 0
if assoc.is_established:
    responses = assoc.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind)
    data = {}
    for (status, identifier) in responses:
        print('---------------------------------------------------------------')
        if status:
            print("Query status: 0x{0:04x}".format(status.Status))
            # If the status is 'Pending' then identifier is the C-FIND response
        else:
            print('Connection timed out, was aborted or received invalid response')
    assoc.release()
else:
    print('Association rejected, aborted or never connected')
