import flask
from flask import Flask, send_file, request, render_template_string, jsonify
from google.cloud import bigquery
import random
from google.cloud import storage
import os


# Define the Google Cloud Storage bucket name
BUCKET_NAME = "bdcc-imagebucket"

# Initialize Google Cloud Storage Client
storage_client = storage.Client()
bucket_name = "bdcc-imagebucket"  # Your GCS bucket name

# Initialize BigQuery Client
bigquery_client = bigquery.Client()
dataset_id = "DatasetBDCC"
table_id = "Images"
full_table_id = f"planar-unity-416918.{dataset_id}.{table_id}"

# Initialize the Google Cloud Storage client
bucket = storage_client.bucket(BUCKET_NAME)

app = Flask(__name__)
bigquery_client = bigquery.Client()

def run_query(query, params=None):
    """Executes a query in BigQuery safely with optional parameters."""
    job_config = bigquery.QueryJobConfig(query_parameters=params) if params else None
    query_job = bigquery_client.query(query, job_config=job_config)
    return query_job.result()


def render_html_table(title, data, headers):
    """Renders an HTML table dynamically for any endpoint."""
    html_template = """
    <html>
    <head>
        <title>{{ title }}</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin: 20px; }
            table { width: 80%; margin: auto; border-collapse: collapse; font-size: 16px; }
            th, td { padding: 10px; border: 1px solid black; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2>{{ title }}</h2>
        {% if data %}
        <table>
            <tr>
                {% for header in headers %}
                <th>{{ header }}</th>
                {% endfor %}
            </tr>
            {% for row in data %}
            <tr>
                {% for value in row %}
                <td>{{ value }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>No records found.</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html_template, title=title, data=data, headers=headers)

def should_return_json():
    """Determines if the request should return JSON (API call) or HTML (browser)."""
    return request.headers.get("Accept") == "application/json" or "curl" in request.headers.get("User-Agent", "")

# 1. GET PATIENT DETAILS (HTML Table)
@app.route("/rest/patients/<int:subject_id>", methods=["GET"])
def get_patient(subject_id):
    """Fetch demographic information of a patient in table format."""
    query = f"""
    SELECT subject_id, gender, dob
    FROM `planar-unity-416918.DatasetBDCC.Patients`
    WHERE subject_id = {subject_id}
    """
    results = run_query(query)
    data = [list(row.values()) for row in results]
    headers = ["Subject ID", "Gender", "Date of Birth"]
    return render_html_table("Patient Details", data, headers)

# 2. LIST ALL ADMISSIONS FOR A PATIENT (HTML Table)
@app.route("/rest/admissions/<int:subject_id>", methods=["GET"])
def get_admissions(subject_id):
    """Returns a list of hospital admissions in table format."""
    query = f"""
    SELECT hadm_id, admittime, dischtime, diagnosis
    FROM `planar-unity-416918.DatasetBDCC.Admissions`
    WHERE subject_id = {subject_id}
    ORDER BY admittime DESC
    """
    results = run_query(query)
    data = [list(row.values()) for row in results]
    headers = ["HADM ID", "Admission Time", "Discharge Time", "Diagnosis"]
    return render_html_table("Admissions List", data, headers)


@app.route("/upload_image", methods=["POST"])
def upload_image():
    """Uploads an image to Google Cloud Storage and stores its metadata in BigQuery."""
    if "image" not in request.files or "subject_id" not in request.form:
        return jsonify({"error": "Image file and subject_id are required"}), 400

    image_file = request.files["image"]
    subject_id = request.form["subject_id"]

    if image_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Upload image to GCS
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"xray/{image_file.filename}")  # Store in 'xray/' directory
    blob.upload_from_file(image_file, content_type=image_file.content_type)

    # Get public URL
    image_url = f"https://storage.googleapis.com/{bucket_name}/xray/{image_file.filename}"

    # Insert into BigQuery
    row = [
        {
            "subject_id": int(subject_id),
            "image_url": image_url,
            "image_name": image_file.filename
        }
    ]

    errors = bigquery_client.insert_rows_json(full_table_id, row)
    if errors:
        return jsonify({"error": "Error inserting data into BigQuery", "details": errors}), 500

    return jsonify({"message": "Image uploaded successfully", "image_url": image_url}), 201


@app.route("/rest/images", methods=["GET"])
def list_all_images():
    """Lists all images stored in BigQuery."""
    query = """
    SELECT subject_id, image_name, image_url
    FROM `planar-unity-416918.DatasetBDCC.Images`
    ORDER BY subject_id ASC
    """

    result = run_query(query)

    images = [{"subject_id": row["subject_id"], "image_name": row["image_name"], "image_url": row["image_url"]} for row
              in result]

    if not images:
        return jsonify({"message": "No images found"}), 404

    return jsonify(images), 200


@app.route("/rest/images/download/<image_name>", methods=["GET"])
def download_image(image_name):
    """Generates a signed URL for an image in Google Cloud Storage."""
    bucket_name = "bdcc-imagebucket"
    blob_name = f"xray/{image_name}"  # Ensure correct path inside the bucket

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    if not blob.exists():
        return jsonify({"error": "Image not found"}), 404

    signed_url = blob.generate_signed_url(expiration=600)  # Valid for 10 mins

    return jsonify({"image_url": signed_url})



# 3. LIST PATIENTS WITH LONGEST STAYS (HTML Table)
@app.route("/rest/patients/longest_stays", methods=["GET"])
def get_longest_stays():
    """Fetches the top 10 patients with the longest hospital stays in table format."""
    query = """
    SELECT subject_id, hadm_id, admittime, dischtime, 
           TIMESTAMP_DIFF(dischtime, admittime, HOUR) AS stay_hours
    FROM `planar-unity-416918.DatasetBDCC.Admissions`
    WHERE dischtime IS NOT NULL
    ORDER BY stay_hours DESC
    LIMIT 10
    """
    results = run_query(query)
    data = [list(row.values()) for row in results]
    headers = ["Subject ID", "HADM ID", "Admission Time", "Discharge Time", "Stay Duration (Hours)"]
    return render_html_table("Longest Hospital Stays", data, headers)

# 4. LIST ALL PATIENTS (HTML Table)
@app.route("/rest/patients", methods=["GET"])
def list_patients():
    """Fetches a limited list of patients in table format."""
    query = """
    SELECT subject_id, gender, dob
    FROM `planar-unity-416918.DatasetBDCC.Patients`
    """
    results = run_query(query)
    data = [list(row.values()) for row in results]
    headers = ["Subject ID", "Gender", "Date of Birth"]
    return render_html_table("Patient List", data, headers)

# 5. CREATE A NEW PATIENT
@app.route("/rest/patients", methods=["POST"])
def create_patient():
    """Inserts a new patient into the Patients table."""
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    # Converter `dob` de "YYYY-MM-DD" para TIMESTAMP no BigQuery
    dob_timestamp = f"{data['dob']} 00:00:00"

    # Verificar se o paciente já existe
    check_query = "SELECT subject_id FROM `planar-unity-416918.DatasetBDCC.Patients` WHERE subject_id = @subject_id"
    params = [bigquery.ScalarQueryParameter("subject_id", "INT64", data['subject_id'])]
    existing = run_query(check_query, params)

    if existing.total_rows > 0:
        return jsonify({"error": "Patient already exists"}), 409  # HTTP 409 Conflict

    # Inserir paciente convertendo DOB para TIMESTAMP corretamente
    insert_query = """
    INSERT INTO `planar-unity-416918.DatasetBDCC.Patients` (subject_id, gender, dob)
    VALUES (@subject_id, @gender, TIMESTAMP(@dob))
    """
    params = [
        bigquery.ScalarQueryParameter("subject_id", "INT64", data['subject_id']),
        bigquery.ScalarQueryParameter("gender", "STRING", data['gender']),
        bigquery.ScalarQueryParameter("dob", "STRING", dob_timestamp)  # Agora como STRING formatada
    ]
    run_query(insert_query, params)

    return jsonify({"message": "Patient added successfully", "data": data}), 201


# 6. CREATE A NEW ADMISSION RECORD
@app.route("/rest/admissions", methods=["POST"])
def create_admission():
    """Inserts a new admission record for a patient."""
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    # Converter `dob` de "YYYY-MM-DD" para TIMESTAMP no BigQuery
    dob_timestamp2 = f"{data['admittime']}"
    dob_timestamp3 = f"{data['dischtime']}"


    # Verificar se a admission já existe
    check_query = "SELECT subject_id FROM `planar-unity-416918.DatasetBDCC.Admissions` WHERE hadm_id = @hadm_id"
    params = [bigquery.ScalarQueryParameter("hadm_id", "INT64", data['hadm_id'])]
    existing = run_query(check_query, params)

    if existing.total_rows > 0:
        return jsonify({"error": "Admission already exists"}), 409  # HTTP 409 Conflict

    insert_query = """
    INSERT INTO `planar-unity-416918.DatasetBDCC.Admissions` (hadm_id, subject_id, admittime, dischtime, diagnosis)
    VALUES (@hadm_id, @subject_id, TIMESTAMP(@admittime), TIMESTAMP(@dischtime), @diagnosis)
    """
    params = [
    bigquery.ScalarQueryParameter("hadm_id", "INT64", data['hadm_id']),
    bigquery.ScalarQueryParameter("subject_id", "INT64", data['subject_id']),
    bigquery.ScalarQueryParameter("admittime", "STRING", dob_timestamp2),
    bigquery.ScalarQueryParameter("dischtime", "STRING", dob_timestamp3),
    bigquery.ScalarQueryParameter("diagnosis", "STRING", data['diagnosis'])
]

    run_query(insert_query, params)

    return jsonify({"message": "Admission added successfully", "data": data}), 201

# 7. UPDATE PATIENT DETAILS
@app.route("/rest/patients/<int:subject_id>", methods=["PUT"])
def update_patient(subject_id):
    """Updates specific patient details dynamically."""
    data = request.get_json(silent=True)

    print("Received Data:", data)

    if not data:
        return jsonify({"error": "No valid JSON data received"}), 400

    update_fields = []
    params = []

    if "gender" in data and data["gender"]:
        update_fields.append("gender = @gender")
        params.append(bigquery.ScalarQueryParameter("gender", "STRING", data["gender"]))

    if "dob" in data and data["dob"]:
        dob_timestamp = f"{data['dob']} 00:00:00"
        update_fields.append("dob = TIMESTAMP(@dob)")
        params.append(bigquery.ScalarQueryParameter("dob", "STRING", dob_timestamp))

    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    query = f"""
    UPDATE `planar-unity-416918.DatasetBDCC.Patients`
    SET {", ".join(update_fields)}
    WHERE subject_id = @subject_id
    """
    params.append(bigquery.ScalarQueryParameter("subject_id", "INT64", subject_id))

    try:
        run_query(query, params)
        return jsonify({"message": "Patient updated successfully", "subject_id": subject_id, "updated_fields": list(data.keys())}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 8. DELETE A PATIENT (CASCADES TO ADMISSIONS)
@app.route("/rest/patients/<int:subject_id>", methods=["DELETE"])
def delete_patient(subject_id):
    """Deletes a patient and anonymizes their admissions."""

    # Primeiro, verificar se o paciente existe
    check_query = "SELECT subject_id FROM `planar-unity-416918.DatasetBDCC.Patients` WHERE subject_id = @subject_id"
    params = [bigquery.ScalarQueryParameter("subject_id", "INT64", subject_id)]
    existing = run_query(check_query, params)

    if existing.total_rows == 0:
        return jsonify({"error": "Patient not found"}), 404

    anonymize_admissions_query = """
    UPDATE `planar-unity-416918.DatasetBDCC.Admissions`
    SET subject_id = NULL
    WHERE subject_id = @subject_id
    """
    run_query(anonymize_admissions_query, params)

    # Excluir o paciente
    delete_patient_query = """
    DELETE FROM `planar-unity-416918.DatasetBDCC.Patients`
    WHERE subject_id = @subject_id
    """
    run_query(delete_patient_query, params)

    return jsonify({"message": f"Patient {subject_id} deleted successfully"}), 200

# 9. DELETE A ADMISSION (CASCADES TO ADMISSIONS)
@app.route("/rest/admissions/<int:hadm_id>", methods=["DELETE"])
def delete_admission(hadm_id):
    """Deletes a admission."""

    # Primeiro, verificar se o admission existe
    check_query = "SELECT hadm_id FROM `planar-unity-416918.DatasetBDCC.Admissions` WHERE hadm_id = @hadm_id"
    params = [bigquery.ScalarQueryParameter("hadm_id", "INT64", hadm_id)]
    existing = run_query(check_query, params)

    if existing.total_rows == 0:
        return jsonify({"error": "Admission not found"}), 404

    # Excluir o paciente
    delete_admission_query = """
    DELETE FROM `planar-unity-416918.DatasetBDCC.Admissions`
    WHERE hadm_id = @hadm_id
    """
    run_query(delete_admission_query, params)

    return jsonify({"message": f"Admission {hadm_id} deleted successfully"}), 200

# 10. Create a new question
@app.route("/rest/patients/<int:subject_id>/question", methods=["POST"])
def create_question(subject_id):
    """Insere uma nova pergunta para um paciente."""
    data = request.json
    if not data or "user_name" not in data or "question_text" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    insert_query = """
    INSERT INTO `planar-unity-416918.DatasetBDCC.Questions` (question_id, subject_id, user_name, question_text, created_at)
    VALUES (COALESCE((SELECT MAX(question_id) FROM `planar-unity-416918.DatasetBDCC.Questions`) + 1, 1), 
            @subject_id, @user_name, @question_text, CURRENT_TIMESTAMP())
    """
    params = [
        bigquery.ScalarQueryParameter("subject_id", "INT64", subject_id),
        bigquery.ScalarQueryParameter("user_name", "STRING", data["user_name"]),
        bigquery.ScalarQueryParameter("question_text", "STRING", data["question_text"]),
    ]

    run_query(insert_query, params)
    return jsonify({"message": "Question added successfully", "data": data}), 201


# Listar todas as perguntas de um paciente em formato de tabela HTML
@app.route("/rest/patients/<int:subject_id>/questions", methods=["GET"])
def get_questions(subject_id):
    """Retorna todas as perguntas feitas a um paciente."""
    query = """
    SELECT user_name, question_text, created_at
    FROM `planar-unity-416918.DatasetBDCC.Questions`
    WHERE subject_id = @subject_id
    ORDER BY created_at DESC
    """
    params = [bigquery.ScalarQueryParameter("subject_id", "INT64", subject_id)]
    result = run_query(query, params)

    data = [list(row.values()) for row in result]
    headers = ["User", "Question", "Date"]

    return render_html_table(f"Questions for Patient {subject_id}", data, headers)

# START SERVER
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
