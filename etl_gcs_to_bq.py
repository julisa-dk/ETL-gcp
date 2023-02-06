from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def extract_from_gcs(color: str, year: int, month: int) -> Path:
    """Download trip data from GCS"""
    gcs_path = f"data/{color}/{color}_tripdata_{year}-{month:02}.parquet"
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"./")
    return Path(f"./{gcs_path}")

@task(log_prints=True)
def print_statement(path: Path) -> pd.DataFrame:
    """Log to print statement"""
    df = pd.read_parquet(path)
    print(f"rows: {len(df)}")
    return df

@task()
def write_bq(df: pd.DataFrame) -> None:
    """Write DataFrame to BigQuery"""

    gcp_credentials_block = GcpCredentials.load("zoom-gcp-creds")

    df.to_gbq(
        destination_table="greentaxiset.rides",
        project_id="serene-column-375413",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append",
    )
    
@flow()
def etl_gcs_to_bq(year: int, month: int, color: str) -> None:
    """Main ETL flow to load data into Big Query"""
    path = extract_from_gcs(color, year, month)
    df = print_statement(path)
    write_bq(df)

@flow()
def etl_param_flow(
     months: list = [2, 3], year: int = 2019, color: str = "yellow"
):
    for month in months:
        etl_gcs_to_bq(year, month, color)

if __name__=="__main__":
    months = [2,3]
    year = 2019
    color = "yellow"
    etl_param_flow()