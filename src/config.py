import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def get_engine():
    user = os.getenv("MYSQL_USER")
    pw = quote_plus(os.getenv("MYSQL_PASSWORD", ""))
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    db = os.getenv("MYSQL_DB", "marketing_db")
    return create_engine(f"mysql+pymysql://{user}:{pw}@{host}:{port}/{db}")