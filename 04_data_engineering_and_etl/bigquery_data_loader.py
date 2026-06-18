# ==============================================================================
# GCP BIGQUERY DATA LOADER
# Automated pipeline to provision Google BigQuery tables and ingest 
# structured data (CSV/DataFrames) using service account credentials.
# ==============================================================================

from dotenv import load_dotenv
import os
from google.cloud import bigquery
import pandas as pd
from google.cloud.exceptions import NotFound

# --- 1. Environment Configuration ---
# Load environment variables from the specified .env file
load_dotenv(dotenv_path='project_info/info.env')

# Retrieve GCP credentials and BigQuery identifiers
service_account_key_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
project_id = os.getenv('PROJECT_ID')
dataset_id = os.getenv('DATASET_ID')
table_id = os.getenv('TABLE_ID')

# --- 2. BigQuery Client Initialization ---
# Authenticate and initialize the BigQuery client using the service account JSON
client = bigquery.Client.from_service_account_json(service_account_key_file)

# Construct the fully qualified table ID
table_id_full = f"{project_id}.{dataset_id}.{table_id}"

# --- 3. Data Loading & Schema Definition ---
# Load local CSV data into a Pandas DataFrame (for verification/processing)
csv_file_path = 'project_info/table_user_reviews.csv'
df = pd.read_csv(csv_file_path)

# Define BigQuery table schema (column names and precise data types)
schema = [
    bigquery.SchemaField("review_id", "STRING"),
    bigquery.SchemaField("user_id", "STRING"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("rating", "INTEGER"),
    bigquery.SchemaField("review_text", "STRING"),
    bigquery.SchemaField("review_date", "DATE")
]

# --- 4. Table Existence Check & Provisioning ---
try:
    # Attempt to retrieve the table to check if it already exists
    client.get_table(table_id_full)  
    print(f"Table '{table_id_full}' already exists.")
except NotFound:
    print(f"Table '{table_id_full}' not found. Initiating creation process...")

    # Provision a new table with the defined schema
    table = bigquery.Table(table_id_full, schema=schema)
    table = client.create_table(table)  
    print(f"✅ Table '{table_id_full}' successfully created.")

# --- 5. Ingestion Job Configuration ---
# Configure the Load Job parameters
job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition="WRITE_TRUNCATE",  # Clear existing table data before loading
    source_format="CSV",                 # Specify source format
    skip_leading_rows=1,                 # Skip the CSV header row
    autodetect=True                      # Enable schema auto-detection fallback
)

# --- 6. Execute Data Load ---
print("Initiating data load job...")

# Load data directly from the CSV file into BigQuery
with open(csv_file_path, "rb") as source_file:
    load_job = client.load_table_from_file(source_file, table_id_full, job_config=job_config)

# Alternative method: Load directly from DataFrame
# load_job = client.load_table_from_dataframe(df, table_id_full, job_config=job_config)

# Block execution until the load job completes
load_job.result()

print(f"🚀 Data successfully ingested into BigQuery table: {table_id_full}")