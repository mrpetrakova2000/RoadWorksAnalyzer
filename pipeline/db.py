import pandas as pd
from sqlalchemy import create_engine
import psycopg2

user = 'postgres'
password = 'postgres'
host = 'localhost'
port = '5432'
database = 'RoadWorksAnalyzer'

def save_in_db(input_df):
    connection_string = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
    engine = create_engine(connection_string)

    df = input_df.copy()
    df.columns = df.columns.str.lower()

    if (create_table_if_not_exists()):
        df.to_sql('road_works', engine, if_exists='append', index=False)

def create_table_if_not_exists():
    db_settings = {
        'dbname': database,
        'user': user,
        'password': password,
        'host': host,
        'port': port
    }       

    create_table_query = """
    CREATE TABLE IF NOT EXISTS road_works (
        global_id BIGSERIAL,
        address TEXT,
        admarea TEXT,
        district TEXT,
        workstype TEXT,
        worksstatus TEXT,
        customer TEXT,
        actualbegindate DATE,
        worksbegindate DATE,
        actualenddate DATE,
        plannedenddate DATE,
        lanes_closed INTEGER,
        geodata TEXT,
        workyear INTEGER
    );
    """

    success = True
    cursor = None
    conn = None
    try:
        conn = psycopg2.connect(**db_settings)
        cursor = conn.cursor()

        cursor.execute(create_table_query)
        conn.commit()

        print("Table 'road_works' create if not exists successfully")

    except Exception as e:
        print(f"Ошибка: {e}")
        success = False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return success