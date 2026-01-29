"""
Tests for the AI Companion Backend
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def auth_token():
    """Create a mock auth token."""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": "test@example.com"})


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns app info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AI Companion"
        assert data["status"] == "running"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_register_user(self, client):
        """Test user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "id" in data

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        # First registration
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user1",
                "password": "password123"
            }
        )
        # Duplicate registration
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user2",
                "password": "password123"
            }
        )
        assert response.status_code == 400


class TestChatEndpoints:
    """Tests for chat endpoints."""

    def test_chat(self, client):
        """Test basic chat functionality."""
        response = client.post(
            "/api/v1/chat/",
            json={
                "message": "Hello, AI Companion!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data


class TestMemoryEndpoints:
    """Tests for memory endpoints."""

    def test_create_memory(self, client):
        """Test creating a memory."""
        response = client.post(
            "/api/v1/memory/",
            json={
                "content": "User's favorite color is blue",
                "memory_type": "semantic",
                "importance": 0.8
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "User's favorite color is blue"
        assert data["memory_type"] == "semantic"
        assert "id" in data

    def test_list_memories(self, client):
        """Test listing memories."""
        # Create a memory first
        client.post(
            "/api/v1/memory/",
            json={
                "content": "Test memory",
                "memory_type": "semantic"
            }
        )
        response = client.get("/api/v1/memory/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAgentEndpoints:
    """Tests for agent endpoints."""

    def test_list_agents(self, client):
        """Test listing agents."""
        response = client.get("/api/v1/agents/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestTaskEndpoints:
    """Tests for task endpoints."""

    def test_create_task(self, client):
        """Test creating a task."""
        response = client.post(
            "/api/v1/tasks/",
            json={
                "description": "Research AI trends",
                "expected_output": "Summary of AI trends"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "task_id" in data
