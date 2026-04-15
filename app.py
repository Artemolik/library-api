from flask import Flask, request, jsonify
import psycopg2

DEFAULT_DB_CONFIG = {
    "dbname": "library_test_db",
    "user": "postgres",
    "password": "secret",
    "host": "localhost",
    "port": 5432,
}


def create_app(db_config=None):
    app = Flask(__name__)
    config = db_config or DEFAULT_DB_CONFIG

    conn = psycopg2.connect(**config)
    cur = conn.cursor()

    # таблиці
    cur.execute("""
    CREATE TABLE IF NOT EXISTS authors (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        birth_year INT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY,
        title TEXT,
        genre TEXT,
        year_published INT,
        created_by TEXT NOT NULL,
        author_id INT REFERENCES authors(id) ON DELETE SET NULL
    )
    """)
    conn.commit()

    # -------- AUTHORS --------

    @app.get("/api/authors")
    def get_authors():
        cur = conn.cursor()
        cur.execute("SELECT id, name, birth_year FROM authors")
        return jsonify(cur.fetchall())

    @app.post("/api/authors")
    def create_author():
        data = request.json
        if not data.get("name"):
            return jsonify({"error": "name required"}), 400

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO authors(name,birth_year) VALUES(%s,%s) RETURNING id",
            (data["name"], data.get("birth_year"))
        )
        conn.commit()
        return jsonify({"id": cur.fetchone()[0], **data}), 201

    @app.get("/api/authors/<int:author_id>")
    def get_author(author_id):
        cur = conn.cursor()
        cur.execute("SELECT id,name,birth_year FROM authors WHERE id=%s", (author_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify({"id": row[0], "name": row[1], "birth_year": row[2]})

    @app.delete("/api/authors/<int:author_id>")
    def delete_author(author_id):
        cur = conn.cursor()
        cur.execute("DELETE FROM authors WHERE id=%s", (author_id,))
        if cur.rowcount == 0:
            return jsonify({"error": "not found"}), 404
        conn.commit()
        return "", 204

    # -------- BOOKS --------

    @app.get("/api/books")
    def get_books():
        genre = request.args.get("genre")

        sql = "SELECT id,title,genre,year_published,created_by,author_id FROM books WHERE 1=1"
        params = []

        if genre:
            sql += " AND genre=%s"
            params.append(genre)

        cur = conn.cursor()
        cur.execute(sql, params)

        return jsonify(cur.fetchall())

    @app.post("/api/books")
    def create_book():
        data = request.json

        if not data.get("title") or not data.get("created_by"):
            return jsonify({"error": "missing"}), 400

        cur = conn.cursor()
        cur.execute("""
        INSERT INTO books(title,genre,year_published,created_by,author_id)
        VALUES(%s,%s,%s,%s,%s)
        RETURNING id
        """, (
            data["title"],
            data.get("genre"),
            data.get("year_published"),
            data["created_by"],
            data.get("author_id"),
        ))

        conn.commit()
        return jsonify({"id": cur.fetchone()[0], **data}), 201

    @app.get("/api/books/<int:book_id>")
    def get_book(book_id):
        cur = conn.cursor()
        cur.execute("SELECT id,title,genre,created_by,author_id FROM books WHERE id=%s", (book_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404

        return jsonify({
            "id": row[0],
            "title": row[1],
            "genre": row[2],
            "created_by": row[3],
            "author_id": row[4],
        })

    @app.delete("/api/books/<int:book_id>")
    def delete_book(book_id):
        cur = conn.cursor()
        cur.execute("DELETE FROM books WHERE id=%s", (book_id,))
        if cur.rowcount == 0:
            return jsonify({"error": "not found"}), 404
        conn.commit()
        return "", 204

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)