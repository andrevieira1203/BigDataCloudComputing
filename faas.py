import functions_framework
import json
from google.cloud import bigquery
from google.cloud import storage
from datetime import datetime, timedelta

# Initialize Google Cloud clients
bigquery_client = bigquery.Client()
storage_client = storage.Client()

# Set up your dataset and table
dataset_id = "DatasetBDCC"
table_id = "Patients"  
full_table_id = f"bdcc25-452114.{dataset_id}.{table_id}"

# Cloud Function entry point
@functions_framework.http
def faas(request):
    """
    Google Cloud Function to perform tasks such as:
    - Periodic computation (e.g., garbage collection)
    - Update tasks (e.g., updating patient status based on long stays)
    """

    try:
        # 1. Example: Get Patients with Long Stays (Update or cleanup task)
        query_long_stays = """
        SELECT subject_id, hadm_id, admittime, dischtime, 
               TIMESTAMP_DIFF(dischtime, admittime, DAY) AS stay_days
        FROM `bdcc25-452114.DatasetBDCC.Admissions`
        WHERE dischtime IS NOT NULL
        AND TIMESTAMP_DIFF(dischtime, admittime, DAY) > 30
        ORDER BY stay_days DESC
        """
        
        # Execute query to get long stay patients
        results_long_stays = bigquery_client.query(query_long_stays).result()

        long_stay_patients = []
        for row in results_long_stays:
            long_stay_patients.append({
                "subject_id": row["subject_id"],
                "hadm_id": row["hadm_id"],
                "admittime": row["admittime"],
                "dischtime": row["dischtime"],
                "stay_days": row["stay_days"]
            })
        
        # 2. Garbage Collection: Clean up old data (e.g., delete inactive records)
        # Clean up records older than 1 year, for example
        one_year_ago = (datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%d")

        query_gc = f"""
        DELETE FROM `bdcc25-452114.DatasetBDCC.Patients`
        WHERE dob < '{one_year_ago}'
        """
        
        # Execute query for garbage collection
        bigquery_client.query(query_gc).result()

        # Build the HTML table response for better visualization
        html_response = "<html><body><h2>Processed Long Stays and Garbage Collection</h2><table border='1'><tr><th>Patient ID</th><th>Admission ID</th><th>Admission Time</th><th>Discharge Time</th><th>Stay Days</th></tr>"

        for patient in long_stay_patients:
            html_response += f"<tr><td>{patient['subject_id']}</td><td>{patient['hadm_id']}</td><td>{patient['admittime']}</td><td>{patient['dischtime']}</td><td>{patient['stay_days']}</td></tr>"

        html_response += "</table><p>Garbage collection executed successfully: Deleted patients older than 1 year.</p></body></html>"

        return html_response

    except Exception as e:
        return f"<html><body><h2>Error</h2><p>{str(e)}</p></body></html>", 500
