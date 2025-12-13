import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv


load_dotenv()

host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")


excel_file = r"C:\Users\DELL\Downloads\sih_test_dataset.xlsx"  
df = pd.read_excel(excel_file)


print(df.head())


print("\n1. Connecting to PostgreSQL...")
try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    cursor = conn.cursor()
    print("✓ PostgreSQL connected successfully")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"✗ PostgreSQL connection failed: {e}")
    exit(1)


engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')
table_name = 'comments_table'  

try:
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print("✅ Excel sheet uploaded to PostgreSQL successfully!")
except Exception as e:
    print(f"✗ Failed to upload Excel to PostgreSQL: {e}")
