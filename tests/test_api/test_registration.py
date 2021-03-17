"""Test registration view."""
import json
from unittest.mock import patch

import pytest

from config import get_settings

settings = get_settings()


def test_normal_registration(test_client, test_session):
    """Test successful login."""
    with patch("views.registration.session", test_session):
        with patch("validators.validation.session", test_session):
            headers = {"Content-Type": "application/json"}
            payload = json.dumps({"username": "newtestuser1", "password": "Qwerty123_"})
            response = test_client.post("api/v1/registration", headers=headers, data=payload)
            assert response.status_code == 201
            assert response.json()


@pytest.mark.parametrize(("username", "password"), [("", ""), (" ", " "), ("testuser1", ""), ("", "Qwerty123_")])
def test_wrong_credentials_registration(test_client, test_session, username, password):
    """Test bad credentials fail."""
    with patch("views.registration.session", test_session):
        with patch("validators.validation.session", test_session):
            payload = json.dumps({"username": username, "password": password})
            headers = {"Content-Type": "application/json"}
            response = test_client.post("api/v1/registration", headers=headers, data=payload)
            assert response.status_code == 400


@pytest.mark.parametrize(("username", "password"), [("testuser1", "Qwerty123_"), ("testuser2", "Qwerty123_")])
def test_usernames_already_used_registration(test_client, test_session, username, password):
    """Test fail to register previously taken usernames."""
    with patch("views.registration.session", test_session):
        with patch("validators.validation.session", test_session):
            payload = json.dumps({"username": username, "password": password})
            headers = {"Content-Type": "application/json"}
            response = test_client.post("api/v1/registration", headers=headers, data=payload)
            assert response.status_code == 400


@pytest.mark.parametrize(
    "password",
    [
        "",
        " ",
        "  ",
        "              ",
        "a",
        "q1!W2@e",
        "q1!W2@e3#R4$t5%",
        "1",
        "1234567",
        "12345678",
        "1.3<5[6]7",
        ",./<>?';:",
        "а",  # russian vowels
        "абвг@д.Е1",  # russian letters
        "abcdefhg",
        "a.b!c@d#e%f&",
        "A.b!c@d#e%f&",
        "abcdefg1",
        "Abcdefg1",
        "1234567a",
        "1234567a.",
        "1234567A.",
        "abcdef1.",
        "ABCDEF1.",
        "абвг@д.Z1",  # russian letters
        "q1!W2@ê3#R",  # french ê
    ],
)
def test_weak_password_registration(test_client, test_session, password):
    """Test fail to register weak passwords."""
    with patch("views.registration.session", test_session):
        with patch("validators.validation.session", test_session):
            payload = json.dumps({"username": "username", "password": password})
            headers = {"Content-Type": "application/json"}
            response = test_client.post("api/v1/registration", headers=headers, data=payload)
            assert response.status_code == 400


if __name__ == "__main__":
    pytest.main()
