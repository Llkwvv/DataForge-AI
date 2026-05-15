
"""Tests for the FastAPI web application."""
import pytest
from fastapi.testclient import TestClient

from mockagent.web.app import app
from mockagent.web.task_manager import task_manager

client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data


class TestTaskLifecycle:
    """Test task creation, status, listing, and cancellation."""

    def test_create_task(self):
        response = client.post(
            "/api/tasks",
            json={
                "sample_filename": "samples/users.csv",
                "table_name": "test_users",
                "rows": 50,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "task_id" in data
        assert data["message"] == "Task created and queued for processing"

    def test_create_task_with_invalid_file(self):
        response = client.post(
            "/api/tasks",
            json={
                "sample_filename": "nonexistent.csv",
                "table_name": "test",
                "rows": 10,
            },
        )
        assert response.status_code == 422  # Validation error

    def test_get_task(self):
        # First create a task
        create_resp = client.post(
            "/api/tasks",
            json={
                "sample_filename": "samples/users.csv",
                "table_name": "test_users",
                "rows": 10,
            },
        )
        task_id = create_resp.json()["task_id"]

        # Then retrieve it
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["task"]["id"] == task_id
        assert data["task"]["sample_filename"] == "samples/users.csv"
        assert data["task"]["table_name"] == "test_users"
        assert data["task"]["rows"] == 10

    def test_get_nonexistent_task(self):
        response = client.get("/api/tasks/nonexistent-id-12345")
        assert response.status_code == 404

    def test_list_tasks(self):
        # Create a few tasks
        for i in range(3):
            client.post(
                "/api/tasks",
                json={
                    "sample_filename": "samples/users.csv",
                    "table_name": f"table_{i}",
                    "rows": 10,
                },
            )

        response = client.get("/api/tasks?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert len(data["tasks"]) >= 3
        assert data["total"] >= 3

    def test_list_tasks_with_limit(self):
        response = client.get("/api/tasks?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) <= 10

    def test_cancel_task(self):
        # Create a task
        create_resp = client.post(
            "/api/tasks",
            json={
                "sample_filename": "samples/users.csv",
                "table_name": "test_users",
                "rows": 10,
            },
        )
        task_id = create_resp.json()["task_id"]

        # Cancel it
        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Task cancelled"

        # Verify status
        task_resp = client.get(f"/api/tasks/{task_id}")
        assert task_resp.json()["task"]["status"] == "cancelled"

    def test_cancel_nonexistent_task(self):
        response = client.delete("/api/tasks/nonexistent-id-12345")
        assert response.status_code == 404


class TestGeneratePreview:
    """Test synchronous preview generation endpoint."""

    def test_generate_preview_default(self):
        response = client.post(
            "/api/generate/preview",
            json={
                "sample_file": "samples/users.csv",
                "rows": 10,
                "table_name": "users",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "sync"
        assert "preview" in data
        assert "fields" in data
        assert "create_table_sql" in data
        assert "preview_rows" in data
        assert len(data["preview_rows"]) <= 5
        assert "CREATE TABLE" in data["create_table_sql"]

    def test_generate_preview_with_defaults(self):
        response = client.post("/api/generate/preview", json={})
        assert response.status_code == 200
        data = response.json()
        assert "preview" in data

    def test_generate_preview_with_rows(self):
        response = client.post(
            "/api/generate/preview",
            json={"rows": 3, "table_name": "test_table"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["preview_rows"]) <= 5


class TestMainPage:
    """Test the main HTML page."""

    def test_index_page(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "MockAgent" in response.text


@pytest.fixture(autouse=True)
def cleanup_tasks():
    """Clear tasks before each test."""
    task_manager.tasks.clear()
    yield
    task_manager.tasks.clear()

