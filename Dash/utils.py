import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import awswrangler as wr
import boto3
import os

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Custom function to format numbers to 2 decimal places
def format_number(n):
    return f'{n:.2f}' if isinstance(n, (float, int)) else n
    

def load_data():
    # Set up your AWS session
    session = boto3.Session(
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name=os.environ['AWS_DEFAULT_REGION']
    )

    # Define your S3 data location (!!!must the most recent ! to do)
    objects = wr.s3.list_directories("s3://bucketsawalle/datasets/")
    objects.sort()
    s3_data_location = objects[-1]

    # Read the data using AWS Data Wrangler
    df = wr.s3.read_parquet(s3_data_location, boto3_session=session)
    df[["TMG_CIF_USD", "TXG_FOB_USD", "TBG_USD"]] = df[["TMG_CIF_USD", "TXG_FOB_USD", "TBG_USD"]].astype(float)
    return df
    