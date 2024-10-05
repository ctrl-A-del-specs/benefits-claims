import os
import pandas as pd
import json
import psycopg2
from sqlalchemy import create_engine

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Database configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "magic")

# Set up the database connection
def create_db_connection():
    conn_str = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(conn_str)
    return engine

# Function to load claims data
def load_claims_data(filepath):
    df = pd.read_csv(filepath)
    return df

# Function to load JSON documents
def load_json_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

# Function to ingest data into PostgreSQL
def ingest_data_to_postgres(df, table_name):
    engine = create_db_connection()
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Data ingested into {table_name} successfully.")

# Function to process and ingest JSON data
def ingest_json_data(json_data, table_name):
    # Convert the JSON data to a DataFrame
    df = pd.json_normalize(json_data)
    ingest_data_to_postgres(df, table_name)

# Main ingestion function
def main():
    # Paths to your data files
    claims_data_path = '/workspaces/uk-benefits-claims/benefits-claims/notebooks/data/claims.csv'
    document_data_path = '/workspaces/uk-benefits-claims/benefits-claims/stream_app/app/document-with-ids.json'
    ground_truth_data_path = '/workspaces/uk-benefits-claims/benefits-claims/stream_app/app/ground-truth-data.csv'
    
    # Load data
    claims_df = load_claims_data(claims_data_path)
    document_data = load_json_data(document_data_path)
    ground_truth_df = load_claims_data(ground_truth_data_path)

    # Ingest claims data
    ingest_data_to_postgres(claims_df, 'claims')

    # Ingest document data
    ingest_json_data(document_data, 'documents')

    # Ingest ground truth data
    ingest_data_to_postgres(ground_truth_df, 'ground_truth')

if __name__ == "__main__":
    main()
