"""Test login view."""
import time
from random import randint
from unittest.mock import patch

import pytest

from config import get_settings

settings = get_settings()


def test_normal_logging_in(test_client, test_session):
    """Test successful login."""
    with patch("validators.authentication.session", test_session):
        with patch("views.login.session", test_session):
            payload = {"username": "testuser1", "password": "Qwerty123_"}
            response = test_client.post("api/v1/login", data=payload)
            assert response.status_code == 200
            assert response.json()["access_token"]


def test_twice_logging_in(test_client, test_session):
    """Test twice successful login but tokens differ."""
    tokens = []
    for _ in range(2):
        with patch("validators.authentication.session", test_session):
            with patch("views.login.session", test_session):
                payload = {"username": "testuser1", "password": "Qwerty123_"}
                response = test_client.post("api/v1/login", data=payload)
                assert response.status_code == 200
        tokens.append(response.json()["access_token"])
        time.sleep(1)
    assert tokens[0] != tokens[1]


def test_only_last_token_is_valid(test_client, test_session):
    """Test only the last obtained token is valid."""
    tokens = []
    for _ in range(randint(2, 10)):
        with patch("validators.authentication.session", test_session):
            with patch("views.login.session", test_session):
                payload = {"username": "testuser1", "password": "Qwerty123_"}
                response1 = test_client.post("api/v1/login", data=payload)
                tokens.append(response1.json()["access_token"])
        time.sleep(1)

    status_codes = []
    for token in tokens:
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                response = test_client.get("/api/v1/items", headers=headers)
                status_codes.append(response.status_code)
    last_code = status_codes.pop()
    assert last_code == 200
    assert set(status_codes) == {401}


@pytest.mark.parametrize(("username", "code"), [("", 422), (" ", 401), ("user1", 401), (1, 401)])
def test_wrong_username(test_client, test_session, username, code):
    """Test login with wrong username."""
    with patch("validators.authentication.session", test_session):
        with patch("views.login.session", test_session):
            payload = {"username": username, "password": "Qwerty123_"}
            response = test_client.post("api/v1/login", data=payload)
            assert response.status_code == code


@pytest.mark.parametrize(("password", "code"), [("", 422), (" ", 401), ("qwerty123_", 401), (1, 401)])
def test_wrong_password(test_client, test_session, password, code):
    """Test login with wrong password."""
    with patch("validators.authentication.session", test_session):
        with patch("views.login.session", test_session):
            payload = {"username": "testuser1", "password": password}
            response = test_client.post("api/v1/login", data=payload)
            assert response.status_code == code


def test_no_credentials(test_client, test_session):
    """Test login with empty credentials."""
    with patch("validators.authentication.session", test_session):
        with patch("views.login.session", test_session):
            payload = {"username": "", "password": ""}
            response = test_client.post("api/v1/login", data=payload)
            assert response.status_code == 422


if __name__ == "__main__":
    pytest.main()
