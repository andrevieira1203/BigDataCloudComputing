import functions_framework
import requests
from google.cloud import bigquery
from google.cloud import storage

# Set up Google Cloud Storage and BigQuery clients
storage_client = storage.Client()
bigquery_client = bigquery.Client()

# The Cloud Function entry point
@functions_framework.http
def faas(request):
    """
    Your Google Cloud Function entry point.
    Perform tasks such as database updates, periodic jobs, etc.
    """

    # Parse the incoming request
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'subject_id' in request_json:
        subject_id = request_json['subject_id']
        hadm_id = request_json.get('hadm_id', None)
        itemid = request_json.get('itemid', None)
        starttime = request_json.get('starttime', None)
        endtime = request_json.get('endtime', None)
        amount = request_json.get('amount', None)
        amountuom = request_json.get('amountuom', None)
        statusdescription = request_json.get('statusdescription', None)
        cgid = request_json.get('cgid', None)

        # Process the data (this is just an example logic)
        if subject_id and hadm_id and itemid:
            try:
                # Example logic: Insert progress record into BigQuery
                query = """
                INSERT INTO `planar-unity-416918.DatasetBDCC.PROGRESS` 
                (subject_id, hadm_id, itemid, starttime, endtime, amount, amountuom, cgid, statusdescription)
                VALUES 
                (@subject_id, @hadm_id, @itemid, TIMESTAMP(@starttime), TIMESTAMP(@endtime), @amount, @amountuom, @cgid, @statusdescription)
                """
                params = [
                    bigquery.ScalarQueryParameter("subject_id", "INT64", subject_id),
                    bigquery.ScalarQueryParameter("hadm_id", "INT64", hadm_id),
                    bigquery.ScalarQueryParameter("itemid", "INT64", itemid),
                    bigquery.ScalarQueryParameter("starttime", "STRING", starttime),  # Convert to STRING if needed
                    bigquery.ScalarQueryParameter("endtime", "STRING", endtime),  # Convert to STRING if needed
                    bigquery.ScalarQueryParameter("amount", "FLOAT64", amount),
                    bigquery.ScalarQueryParameter("amountuom", "STRING", amountuom),
                    bigquery.ScalarQueryParameter("cgid", "INT64", cgid),
                    bigquery.ScalarQueryParameter("statusdescription", "STRING", statusdescription),
                ]

                # Execute query
                bigquery_client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))

                return "Progress record added successfully!", 200
            except Exception as e:
                return f"Error: {str(e)}", 500
        else:
            return "Missing required fields", 400
    else:
        return "Invalid JSON", 400
