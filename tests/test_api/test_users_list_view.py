"""Test users_list view."""
from unittest.mock import patch

from config import get_settings
import pytest

settings = get_settings()


def test_get_users_list(test_client, test_session, token):
    """Test users list view sends 200 & users."""
    with patch("validators.authentication.session", test_session):
        with patch("views.users_list.session", test_session):
            headers = {"Authorization": f"Bearer {token}"}
            response = test_client.get("/api/v1/users", headers=headers)
            assert response.status_code == 200
            users = response.json()
            assert users["existing_users"]


def test_not_get_users_list_invalid_token(test_client, test_session, token):
    """Test users list view sends 401 for invalid token."""
    with patch("validators.authentication.session", test_session):
        with patch("views.users_list.session", test_session):
            headers = {"Authorization": f"Bearer {token}+a"}
            response = test_client.get("/api/v1/users", headers=headers)
            assert response.status_code == 401


def test_not_get_users_list_no_auth(test_client, test_session, token):
    """Test users list view sends 401 without token."""
    with patch("validators.authentication.session", test_session):
        with patch("views.users_list.session", test_session):
            response = test_client.get("/api/v1/users")
            assert response.status_code == 401


if __name__ == "__main__":
    pytest.main()
