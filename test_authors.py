class TestAuthors:
    def test_get_authors_empty(self, client):
        res = client.get("/api/authors")
        assert res.status_code == 200
        assert res.get_json() == []

    def test_create_author(self, client):
        res = client.post("/api/authors", json={
            "name": "Тарас Шевченко",
            "birth_year": 1814
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data["name"] == "Тарас Шевченко"
        assert "id" in data

    def test_create_author_without_name(self, client):
        res = client.post("/api/authors", json={})
        assert res.status_code == 400

    def test_get_author_by_id(self, client):
        author = client.post("/api/authors", json={
            "name": "Test"
        }).get_json()

        res = client.get(f"/api/authors/{author['id']}")
        assert res.status_code == 200

    def test_get_author_not_found(self, client):
        res = client.get("/api/authors/999")
        assert res.status_code == 404

    def test_delete_author(self, client):
        author = client.post("/api/authors", json={
            "name": "X"
        }).get_json()

        res = client.delete(f"/api/authors/{author['id']}")
        assert res.status_code == 204

    def test_delete_author_not_found(self, client):
        res = client.delete("/api/authors/999")
        assert res.status_code == 404