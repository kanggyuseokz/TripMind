import os

user = os.getenv("DB_USER")
pwd  = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT", "3306")
name = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{name}?charset=utf8mb4"
)