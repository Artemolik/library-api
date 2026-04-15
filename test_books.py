class TestBooks:
    def test_get_books_empty(self, client):
        res = client.get("/api/books")
        assert res.status_code == 200
        assert res.get_json() == []

    def test_create_book(self, client):
        res = client.post("/api/books", json={
            "title": "Kobzar",
            "created_by": "Ім'я Прізвище"
        })
        assert res.status_code == 201

    def test_create_book_without_title(self, client):
        res = client.post("/api/books", json={
            "created_by": "Ім'я Прізвище"
        })
        assert res.status_code == 400

    def test_create_book_without_created_by(self, client):
        res = client.post("/api/books", json={
            "title": "Test"
        })
        assert res.status_code == 400


class TestBooksFilter:
    def test_filter_by_genre(self, client):
        client.post("/api/books", json={
            "title": "Kobzar",
            "genre": "poetry",
            "created_by": "Ім'я Прізвище"
        })

        client.post("/api/books", json={
            "title": "Novel",
            "genre": "novel",
            "created_by": "Ім'я Прізвище"
        })

        res = client.get("/api/books?genre=poetry")
        data = res.get_json()

        assert len(data) == 1
        assert data[0]["title"] == "Kobzar"