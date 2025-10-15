import psycopg2
import os

DB_HOST = "localhost"
DB_NAME = "SmartSurveillanceSystem"
DB_USER = "postgres"
DB_PASS = "123"

def get_db_conn():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

MESSAGE_IMG_DIR = os.path.join(os.path.dirname(__file__), "message_images")