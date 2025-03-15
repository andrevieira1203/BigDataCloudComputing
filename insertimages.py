from google.cloud import bigquery

# Define your Google Cloud project and dataset
PROJECT_ID = "planar-unity-416918"
DATASET_ID = "DatasetBDCC"
TABLE_ID = "Images"
DATASET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Initialize BigQuery Client
bq_client = bigquery.Client()

# Define the schema for the Images table
TABLE_SCHEMA = [
    bigquery.SchemaField("subject_id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("image_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("image_url", "STRING", mode="REQUIRED"),
]

def insert_images_into_bigquery():
    """Insert image data into BigQuery."""
    image_data = [
        {"subject_id": 3369, "image_name": "xray1.png", "image_url": "https://storage.googleapis.com/bdcc-imagebucket/xray/xray1.png"},
        {"subject_id": 74869, "image_name": "xray2.png", "image_url": "https://storage.googleapis.com/bdcc-imagebucket/xray/xray2.png"},
        {"subject_id": 10484, "image_name": "xray3.png", "image_url": "https://storage.googleapis.com/bdcc-imagebucket/xray/xray3.png"}
    ]

    errors = bq_client.insert_rows_json(DATASET_TABLE, image_data)

    if errors:
        print(f"❌ Error inserting data into BigQuery: {errors}")
    else:
        print("✅ Images inserted successfully into BigQuery.")

insert_images_into_bigquery()




