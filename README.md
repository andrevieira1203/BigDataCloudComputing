# Big Data & Cloud Computing : Hospital Backend System on GCP

## Description

This project was developed for the **Big Data and Cloud Computing (BDCC)** course, with the goal of understanding how **cloud computing services** can be used to build applications that are **scalable, fast, and highly available**.

It consists of the design and implementation of a **backend system for a hospital electronic health records (EHR) platform**, modeled after the **MIMIC-III** clinical database. The project includes a web application, a Function-as-a-Service (FaaS) component, scheduled jobs, load testing scripts, and a full BigQuery database setup on **Google Cloud Platform (GCP)**.

---

## Repository Structure

```
BigDataCloudComputing/
│
├── main.py                  # Application entry point
├── app2.py                  # Application iteration 2
├── app3.py                  # Application iteration 3
├── web.py                   # Web server - initial version
├── web2.py                  # Web server - iteration 2
├── web3.py                  # Web server - iteration 3
├── webfinal.py              # Web server - final version
├── faas.py                  # Function-as-a-Service (Google Cloud Functions)
├── insertimages.py          # Script to insert images into Cloud Storage / BigQuery
├── load_test.yml            # Load testing configuration (Locust)
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## Architecture Overview

The system is built on **Google Cloud Platform (GCP)** and leverages the following services:

| GCP Service | Role |
|---|---|
| **BigQuery** | Data warehouse for hospital records (MIMIC-III) |
| **Cloud Storage** | Storage for medical images |
| **Cloud Functions** | FaaS component for scheduled/event-driven tasks |
| **Cloud Scheduler** | Periodic execution of the FaaS function |

---

## Database Setup (BigQuery)

Before running the application, the required BigQuery tables must be created. The project name and bucket name must be updated to match your GCP project.

### Table: `Questions`
```sql
CREATE TABLE <your-project>.DatasetBDCC.Questions (
  question_id   INT64     NOT NULL,
  subject_id    INT64     NOT NULL,
  user_name     STRING    NOT NULL,
  question_text STRING    NOT NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### Table: `Progress`
```sql
CREATE TABLE <your-project>.DatasetBDCC.Progress (
  subject_id          INT64,
  hadm_id             INT64,
  itemid              INT64,
  starttime           TIMESTAMP,
  endtime             TIMESTAMP,
  amount              FLOAT64,
  amountuom           STRING,
  cgid                INT64,
  statusdescription   STRING
);

-- Populate from MIMIC-III Inputevents_mv
INSERT INTO <your-project>.DatasetBDCC.Progress
  (subject_id, hadm_id, itemid, starttime, endtime, amount, amountuom, cgid, statusdescription)
SELECT
  subject_id, hadm_id, itemid, starttime, endtime, amount, amountuom, cgid, statusdescription
FROM <your-project>.DatasetBDCC.Inputevents_mv
WHERE subject_id IS NOT NULL
  AND hadm_id   IS NOT NULL
  AND itemid    IS NOT NULL
  AND starttime IS NOT NULL;
```

### Table: `Images`
```sql
CREATE TABLE <your-project>.DatasetBDCC.Images (
  subject_id   INT64,
  image_name   STRING,
  image_url    STRING
);
```

---

## FaaS & Cloud Scheduler Setup

The `faas.py` function is deployed as a **Google Cloud Function** and triggered periodically via **Cloud Scheduler**.

### Deploy the Cloud Function
```bash
gcloud functions deploy faas \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --gen2 \
  --region us-central1
```

### Create the Scheduler Job (daily at 9:00 AM Lisbon time)
```bash
gcloud scheduler jobs create http faas-job \
  --schedule "0 9 * * *" \
  --time-zone "Europe/Lisbon" \
  --uri "https://us-central1-<your-project>.cloudfunctions.net/faas" \
  --http-method "GET" \
  --description "Job to execute FaaS periodically" \
  --location "us-central1"
```

---

## Getting Started

### Prerequisites
- A **Google Cloud Platform** account with a project set up
- The **Google Cloud SDK** (`gcloud`) installed
- Python 3.9+

### 1. Clone the repository
```bash
git clone https://github.com/andrevieira1203/BigDataCloudComputing.git
cd BigDataCloudComputing
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up GCP credentials
```bash
# Linux / macOS
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your_credentials.json"

# Windows (PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\YourUser\Desktop\your_credentials.json"
```

### 4. Update project references
Replace all occurrences of the project ID and bucket name in the source files with your own GCP project ID.

### 5. Run the application
```bash
python main.py
```

---

## Load Testing

Load testing is configured via `load_test.yml`, likely using **Locust** or a similar tool.

```bash
# Example with Locust
locust -f load_test.yml
```

---

## 🛠️ Technologies & Services

- **Python 3** — backend development
- **Google BigQuery** — cloud data warehouse
- **Google Cloud Functions** — serverless FaaS
- **Google Cloud Storage** — image storage
- **Google Cloud Scheduler** — cron-based job scheduling
- **MIMIC-III** — clinical database used as data source
- **Locust** — load testing

---

## Languages

| Language | Percentage |
|---|---|
| Python | 100% |

---

## Important Notes

- The **GCP project ID** and **bucket name** must be updated to match your own GCP project before running any scripts.
- The **MIMIC-III** dataset requires credentialed access — request access at [PhysioNet](https://physionet.org/content/mimiciii/1.4/).
- Never commit your `credentials.json` file to version control — add it to `.gitignore`.

---
