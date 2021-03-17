"""Test login view."""
from unittest.mock import patch

from sqlalchemy.future import select

from config import get_settings
import pytest

from database.models import User, UserToken
from validators.authentication import decode_token

settings = get_settings()


def test_normal_logging_in(test_client, test_session):
    """Test successful login."""
    with patch("validators.authentication.session", test_session):
        with patch("views.login.session", test_session):
            payload = {"username": "testuser1", "password": "Qwerty123_"}
            response = test_client.post("api/v1/login", data=payload)
            assert response.status_code == 200
            assert response.json()["access_token"]


#
# @pytest.mark.asyncio
# async def test_token_stored_in_database(test_client, test_session):
#     """Test token was stored in database."""
#     with patch("validators.authentication.session", test_session):
#         with patch("views.login.session", test_session):
#             payload = {'username': "testuser1",
#                        "password": "Qwerty123_"}
#             response = test_client.post('api/v1/login', data=payload).json()
#             token = response['access_token']
#             payload = decode_token(token, settings.SECRET_KEY)
#             async with test_session:
#                 query = select(UserToken.token).where(UserToken.user_id == payload['id'])
#                 result = await test_session.execute(query)
#                 assert result.scalars().first()


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
    """Test login with wrong username."""
    with patch("validators.authentication.session", test_session):
        with patch("views.login.session", test_session):
            payload = {"username": "testuser1", "password": password}
            response = test_client.post("api/v1/login", data=payload)
            assert response.status_code == code


def test_no_credentials(test_client, test_session):
    """Test login with wrong username."""
    with patch("validators.authentication.session", test_session):
        with patch("views.login.session", test_session):
            payload = {"username": "", "password": ""}
            response = test_client.post("api/v1/login", data=payload)
            assert response.status_code == 422


if __name__ == "__main__":
    pytest.main()
