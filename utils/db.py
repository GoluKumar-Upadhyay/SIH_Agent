import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("POSTGRES_PORT")
    )

def run_sql(sql):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    df = pd.DataFrame(rows, columns=columns)

    cursor.close()
    conn.close()
    return df
