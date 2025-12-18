import os
import boto3
import snowflake.connector
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -------- MinIO Config --------
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET = os.getenv("MINIO_BUCKET")
LOCAL_DIR = os.getenv("MINIO_LOCAL_DIR", "/tmp/minio_downloads")

# -------- Snowflake Config --------
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DB = os.getenv("SNOWFLAKE_DB")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

TABLES = ["customers", "accounts", "transactions"]


def download_from_minio():
    os.makedirs(LOCAL_DIR, exist_ok=True)

    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY
    )

    result = {}

    for table in TABLES:
        prefix = f"{table}/"
        resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
        objects = resp.get("Contents", [])

        result[table] = {
            "files": [],
            "keys": []
        }

        for obj in objects:
            key = obj["Key"]
            filename = os.path.basename(key)
            local_file = os.path.join(LOCAL_DIR, filename)

            s3.download_file(BUCKET, key, local_file)

            print(f"📥 Downloaded {key} → {local_file}")

            result[table]["files"].append(local_file)
            result[table]["keys"].append(key)

    return result


def move_processed_files(source_keys):
    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY
    )

    print("Moving processed files to MinIO processed/ folder")

    for key in source_keys:
        new_key = f"processed/{key}"

        print(f"➡️ {key} → {new_key}")

        s3.copy_object(
            Bucket=BUCKET,
            CopySource={"Bucket": BUCKET, "Key": key},
            Key=new_key
        )

        s3.delete_object(Bucket=BUCKET, Key=key)

    print("✅ Files moved to processed/")



def load_to_snowflake(**context):
    data = context["ti"].xcom_pull(task_ids="download_minio")
    if not data:
        print("No files found in MinIO.")
        return

    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DB,
        schema=SNOWFLAKE_SCHEMA,
    )
    cur = conn.cursor()

    print("✅ Connected to Snowflake")

    try:
        for table, payload in data.items():
            files = payload["files"]
            keys = payload["keys"]

            if not files:
                print(f"No files for {table}, skipping.")
                continue

            for f in files:
                cur.execute(f"PUT file://{f} @%{table}")
                print(f"⬆️ Uploaded {f} → @{table}")

            cur.execute(f"""
                COPY INTO {table}
                FROM @%{table}
                FILE_FORMAT=(TYPE=PARQUET)
                ON_ERROR='CONTINUE'
            """)

            print(f"📊 Data loaded into {table}")

            # Move files only after successful COPY
            move_processed_files(keys)

        conn.commit()

    finally:
        cur.close()
        conn.close()




# --------------------------------------------------
# Airflow DAG
# --------------------------------------------------
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="minio_to_snowflake_banking",
    default_args=default_args,
    description="Load MinIO parquet into Snowflake RAW tables and archive processed files",
    schedule_interval="*/30 * * * *",  # every 30 minutes
    start_date=datetime(2025, 11, 1),
    catchup=False,
) as dag:

    download_task = PythonOperator(
        task_id="download_minio",
        python_callable=download_from_minio,
    )

    load_task = PythonOperator(
        task_id="load_snowflake",
        python_callable=load_to_snowflake,
        provide_context=True,
    )

    download_task >> load_task