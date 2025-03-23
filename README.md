# BigDataCloudComputing
The goal of this project is to understand how services available in cloud computing platforms can
be used for creating applications that are scalable, fast, and highly available. It consists in the design and implementation of the backend for a hospital system like
hospital electronic health record databases as in the MIMIC-III database, and companion testing
scripts.

# O bucket, assim como o o nome do projeto tem que ser mudado para o do utilizador;

#  $env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\Utilizador\Desktop\your_credentials.json" 
Código necessário para definir as credenciais necessárias.

# Código de SQL para criar as tabelas necessárias no bigQuery

### Tabela "Questions"
CREATE TABLE bdcc25-452114.DatasetBDCC.Questions (
    question_id INT64 NOT NULL,
    subject_id INT64 NOT NULL,
    user_name STRING NOT NULL,  
    question_text STRING NOT NULL,  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),  
);

### Tabela "Progress" e inserção de dados 
CREATE TABLE bdcc25-452114.DatasetBDCC.Progress (
    subject_id INT64,
    hadm_id INT64,
    itemid INT64,
    starttime TIMESTAMP,
    endtime TIMESTAMP,
    amount FLOAT64,
    amountuom STRING,
    cgid INT64,
    statusdescription STRING
);


INSERT INTO bdcc25-452114.DatasetBDCC.Progress (subject_id, hadm_id, itemid, starttime, endtime, amount, amountuom, cgid, statusdescription)
SELECT
    subject_id,
    hadm_id,
    itemid,
    starttime,
    endtime,
    amount,
    amountuom,
    cgid,
    statusdescription
FROM bdcc25-452114.DatasetBDCC.Inputevents_mv
WHERE subject_id IS NOT NULL
  AND hadm_id IS NOT NULL
  AND itemid IS NOT NULL
  AND starttime IS NOT NULL;

### Tabela "Images"
CREATE TABLE bdcc25-452114.DatasetBDCC.Images (
  subject_id INT64,
  image_name STRING,
  image_url STRING
);

# FaaS and Google Schedule
Código para ter o link do faas: gcloud functions deploy faas --runtime python39 --trigger-http --allow-unauthenticated --gen2 --region us-central1
gcloud scheduler jobs create http faas-job --schedule "0 9 * * *" --time-zone "Europe/Lisbon" --uri "https://us-central1-bdcc25-452114.cloudfunctions.net/faas" --http-method "GET" --description "Job to execute FaaS periodically" --location "us-central1"