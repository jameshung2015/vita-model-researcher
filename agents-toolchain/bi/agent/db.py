import os
from sqlalchemy import create_engine

PG_URL = (
    f"postgresql+psycopg://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@"
    f"{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
)
engine = create_engine(PG_URL, pool_pre_ping=True)

