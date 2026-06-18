# ==============================================================================
# GCP BIGQUERY DATA ANALYSIS & TRANSFORMATION
# Executes SQL queries on BigQuery tables to aggregate product ratings, 
# filter negative reviews, and write the transformed DataFrames back to GCP.
# ==============================================================================

from google.cloud import bigquery
from dotenv import load_dotenv
import os
from pandas_gbq import to_gbq  # Recommended by Google for Pandas-to-BQ operations

# ==============================================================================
# PHASE 1: ENVIRONMENT SETUP & CLIENT INITIALIZATION
# ==============================================================================

# Load environment variables from the .env configuration file
load_dotenv(dotenv_path='project_info/info.env')
service_account_key_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
project_id = os.getenv('PROJECT_ID')
dataset_id = os.getenv('DATASET_ID')
table_id = os.getenv('TABLE_ID')

# Initialize the BigQuery client using the service account JSON key
client = bigquery.Client.from_service_account_json(service_account_key_file)

# Construct the fully qualified table identifier
full_table = f"{project_id}.{dataset_id}.{table_id}"

# ==============================================================================
# PHASE 2: DATA AGGREGATION (AVERAGE PRODUCT RATING)
# ==============================================================================

# SQL query to calculate the average rating per product, sorted in descending order
query_1 = f"""
SELECT product_id, ROUND(AVG(rating), 2) AS avg_rating
FROM `{full_table}`
GROUP BY 1
ORDER BY 2 DESC
"""

# Execute the query and convert the result into a Pandas DataFrame
df_avg = client.query(query_1).result().to_dataframe()

print("📊 Average Product Ratings:")
print(df_avg)

# Define target table for aggregated data (shortened format for pandas_gbq)
avg_rating_table = f"{dataset_id}.avg_product_rating"

# Write the aggregated DataFrame back to a new BigQuery table
to_gbq(df_avg, avg_rating_table, project_id=project_id, if_exists='replace')
print(f"✅ Successfully written to table: {avg_rating_table}")

# ==============================================================================
# PHASE 3: DATA FILTERING (NEGATIVE REVIEWS EXTRACTION)
# ==============================================================================

# SQL query to extract all reviews with a rating of 2 or lower
query_2 = f"""
SELECT *
FROM `{full_table}`
WHERE rating <= 2
"""

# Execute the query and load results into a DataFrame
df_negative = client.query(query_2).result().to_dataframe()

print("\n⚠️ Negative Reviews (Rating <= 2):")
print(df_negative)

# Define target table for negative reviews
negative_table = f"{dataset_id}.negative_reviews"

# Overwrite the target table with the filtered DataFrame
to_gbq(df_negative, negative_table, project_id=project_id, if_exists='replace')
print(f"♻️ Table overwritten successfully: {project_id}.{negative_table}")

# ==============================================================================
# PHASE 4: VERIFICATION & READ-BACK
# ==============================================================================

# SQL query to read back the newly created negative_reviews table
query_negative_reviews = f"""
SELECT *
FROM `{project_id}.{negative_table}`
"""

# Fetch the updated table to verify the load operation
df_negative_reviews = client.query(query_negative_reviews).result().to_dataframe()

print("\n📋 Updated 'negative_reviews' table contents:")
print(df_negative_reviews)