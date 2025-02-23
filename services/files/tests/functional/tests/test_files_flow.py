import uuid
from io import BytesIO


def test_ping(client, mock_redis_repo):
    response = client.get("/api/v1/files/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_files(client, test_user_id, mock_redis_repo):
    response = client.get("/api/v1/files/")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "files" in data
    assert data["user_id"] == str(test_user_id)


def test_upload_file(client, mock_redis_repo):
    test_file = BytesIO(b"test content")
    test_file.name = "test.txt"

    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("test.txt", test_file)},
        data={"path": "/test/path", "user_id": str(uuid.uuid4()), "bucket": "test-bucket"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "test.txt"
    assert "path" in data
    assert data["size"] > 0


def test_download_file(client, mock_redis_repo):
    file_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/files/download/?path={file_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


def test_get_revisions(client, mock_redis_repo):
    response = client.get("/api/v1/files/revisions/?path=/test/path&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
