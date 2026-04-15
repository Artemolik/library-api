import pytest
import psycopg2
from app import create_app

TEST_DB = {
    "dbname": "library_test_db",
    "user": "postgres",
    "password": "secret",
    "host": "localhost",
    "port": 5432,
}


@pytest.fixture(scope="session")
def app():
    return create_app(TEST_DB)


@pytest.fixture(scope="session")
def test_db():
    conn = psycopg2.connect(**TEST_DB)
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def client(app, test_db):
    cur = test_db.cursor()
    cur.execute("TRUNCATE books, authors RESTART IDENTITY CASCADE;")
    test_db.commit()

    return app.test_client()