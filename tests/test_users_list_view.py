"""Test users_list view."""
from unittest.mock import patch

import pytest


@pytest.mark.xfail(reason="token required")
def test_get_users_list(test_client, database):
    """Test users list view sends 200 & users."""
    with patch("views.users_list.session", database):
        response = test_client.get("/api/v1/users")
        assert response.status_code == 200
        users = response.json()
        assert users["existing_users"]


def test_post_users_list(test_client, database):
    """Test POST method is not allowed."""
    response = test_client.post("/api/v1/users")
    assert response.status_code == 405


def test_put_users_list(test_client, database):
    """Test PUT method is not allowed."""
    response = test_client.put("/api/v1/users")
    assert response.status_code == 405


def test_patch_users_list(test_client, database):
    """Test PATCH method is not allowed."""
    response = test_client.patch("/api/v1/users")
    assert response.status_code == 405


def test_delete_users_list(test_client, database):
    """Test DELETE method is not allowed."""
    response = test_client.delete("/api/v1/users")
    assert response.status_code == 405


if __name__ == "__main__":
    pytest.main()
