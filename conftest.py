import os
import time
import pytest
import psycopg2
from app import create_app

# Зчитування конфігурації з ENV з fallback на локальні значення
TEST_DB_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "port": int(os.environ.get("POSTGRES_PORT", "5432")),
    "database": os.environ.get("POSTGRES_DB", "library_test_db"),
    "user": os.environ.get("POSTGRES_USER", "postgres"),
    "password": os.environ.get("POSTGRES_PASSWORD", "secret"),
}

# Функція очікування готовності PostgreSQL
def wait_for_db():
    retries = 12
    for i in range(retries):
        try:
            conn = psycopg2.connect(**TEST_DB_CONFIG)
            conn.close()
            print("Connected to PostgreSQL!")
            return True
        except psycopg2.OperationalError:
            print(f"DB not ready, retry {i+1}/{retries}...")
            time.sleep(5)
    raise Exception("Cannot connect to PostgreSQL")

# Виклик перед тестами
wait_for_db()

@pytest.fixture
def app():
    app = create_app(TEST_DB_CONFIG)
    return app

@pytest.fixture
def client(app):
    return app.test_client()