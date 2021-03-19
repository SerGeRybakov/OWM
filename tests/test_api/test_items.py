"""Test items view."""
import json
from unittest.mock import patch

import pytest

from config import get_settings
from views.login import create_access_token

settings = get_settings()


class TestGetItems:
    """Test the work of users' items list get method."""

    @staticmethod
    def test_get_user_items(test_client, test_session, token):
        """Test items items view sends 200 & items."""
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                response = test_client.get("/api/v1/items", headers=headers)
                assert response.status_code == 200
                assert response.json()["testuser1"]

    @staticmethod
    def test_get_user_items_unauthorized(test_client, exchange_link):
        """Test view sends 401 for unauthorized user."""
        response = test_client.get("/api/v1/items")
        assert response.status_code == 401

    @staticmethod
    def test_get_users_items_invalid_token(test_client, test_session, token):
        """Test view sends 401 for invalid token."""
        with patch("validators.authentication.session", test_session):
            with patch("views.users_list.session", test_session):
                headers = {"Authorization": f"Bearer {token}+a"}
                response = test_client.get("/api/v1/items", headers=headers)
                assert response.status_code == 401

    @staticmethod
    def test_get_user_items_still_works(test_client, test_session, token):
        """Test items get-view sends 200 & items even if there's any other query in the path."""
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                response = test_client.get("/api/v1/items?q=1", headers=headers)
                assert response.status_code == 200
                assert response.json()


class TestCreateNewItem:
    """Test the work of item creation method."""

    @staticmethod
    def test_create_new_item(test_client, test_session, token):
        """Test create new item."""
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                payload = json.dumps({"title": "new_awesome_item"})
                response = test_client.post("/api/v1/items/new", headers=headers, data=payload)
                assert response.status_code == 201
                assert response.json()

    @staticmethod
    def test_create_new_item_unauthorized(test_client, exchange_link):
        """Test view sends 401 for unauthorized user."""
        response = test_client.post("/api/v1/items/new")
        assert response.status_code == 401

    @staticmethod
    def test_create_new_item_invalid_token(test_client, test_session, token):
        """Test view sends 401 for invalid token."""
        with patch("validators.authentication.session", test_session):
            with patch("views.users_list.session", test_session):
                headers = {"Authorization": f"Bearer {token}+a"}
                response = test_client.post("/api/v1/items/new", headers=headers)
                assert response.status_code == 401

    @staticmethod
    def test_create_new_item_with_the_same_title(test_client, test_session, token):
        """Test fail to create more than 1 item with the same title."""
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                payload = json.dumps({"title": "new_awesome_item"})
                test_client.post("/api/v1/items/new", headers=headers, data=payload)
                response = test_client.post("/api/v1/items/new", headers=headers, data=payload)
                assert response.status_code == 400
                assert response.json()


class TestDeleteItem:
    """Test the work of delete method."""

    @staticmethod
    def test_delete_one_item(test_client, test_session, token):
        """Test delete one item by id."""
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                response = test_client.delete("/api/v1/items/:1", headers=headers)
                assert response.status_code == 200  # Actually it should be 204
                assert "successfully deleted" in response.json()["message"]

    @staticmethod
    def test_delete_one_item_unauthorized(test_client):
        """Test view sends 401 for unauthorized user."""
        response = test_client.delete("/api/v1/items/:1")
        assert response.status_code == 401

    @staticmethod
    def test_delete_one_item_invalid_token(test_client, test_session, token):
        """Test view sends 401 for invalid token."""
        with patch("validators.authentication.session", test_session):
            with patch("views.users_list.session", test_session):
                headers = {"Authorization": f"Bearer {token}+a"}
                response = test_client.delete("/api/v1/items/:2", headers=headers)
                assert response.status_code == 401

    @staticmethod
    def test_twice_delete_one_item(test_client, test_session, token):
        """Test fail to delete one item twice."""
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                test_client.delete("/api/v1/items/:2", headers=headers)

                response = test_client.delete("/api/v1/items/:2", headers=headers)
                assert response.status_code == 404


class TestExchange:
    """Test the work of exchange methods."""

    @staticmethod
    @pytest.mark.parametrize("item_id", [1, 2, "1", "2"])
    def test_send(test_client, test_session, token, item_id):
        """Test send view creates a link for an item transfer."""
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                transfer_data = {"item_id": item_id, "achiever": "testuser2"}
                payload = json.dumps(transfer_data)
                response = test_client.post("/api/v1/send", headers=headers, data=payload)
                message = response.json()
                assert response.status_code == 200
                assert "/api/v1/get?transfer_key=eyJ" in message["link"]

    @staticmethod
    @pytest.mark.parametrize(
        "item_id", [-1, 0, 10, "-1", "0", "10", "", " ", "\n", "one", [1], (1,), [1, 2], {"id": 1}]
    )
    def test_send_returns_fail_on_item(test_client, test_session, token, item_id):
        """Test send view returns 400 or 422 due to wrong or absent item_id."""
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                transfer_data = {"item_id": item_id, "achiever": "testuser2"}
                payload = json.dumps(transfer_data)
                response = test_client.post("/api/v1/send", headers=headers, data=payload)
                assert response.status_code in (400, 422)

    @staticmethod
    @pytest.mark.parametrize("achiever", [-1, 0, 10, "-1", "0", "10", "", " ", "\n", "one", "user1", "testuser1"])
    def test_send_returns_fail_on_achiever(test_client, test_session, token, achiever):
        """Test send view returns 400 or 422 due to wrong or absent achiever."""
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                transfer_data = {"item_id": 1, "achiever": achiever}
                payload = json.dumps(transfer_data)
                response = test_client.post("/api/v1/send", headers=headers, data=payload)
                assert response.status_code in (400, 422)

    @staticmethod
    def test_get_item_transfer(test_client, test_session, exchange_link, token):
        """Test successful item transfer."""
        # login testuser2 and get his access_token
        with patch("validators.authentication.session", test_session):
            with patch("views.login.session", test_session):
                payload = {"username": "testuser2", "password": "Qwerty123-"}
                response = test_client.post("api/v1/login", data=payload).json()
        token = response["access_token"]

        # testuser2 follows the link to obtain item1-1
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                response = test_client.get(exchange_link, headers=headers)
                assert response.status_code == 200
                assert response.json()["message"] == "You've just obtained item1-1"

    @staticmethod
    def test_get_item_transfer_twice(test_client, test_session, exchange_link):
        """Test one item can't be obtained more than once."""
        # login testuser2 and get his access_token
        with patch("validators.authentication.session", test_session):
            with patch("views.login.session", test_session):
                payload = {"username": "testuser2", "password": "Qwerty123-"}
                response = test_client.post("api/v1/login", data=payload).json()
        token = response["access_token"]

        for _ in range(2):
            with patch("validators.authentication.session", test_session):
                with patch("views.items.session", test_session):
                    headers = {"Authorization": f"Bearer {token}"}
                    response = test_client.get(exchange_link, headers=headers)
        assert response.status_code == 400
        assert response.json()["detail"] == "Item item1-1 is already yours"

    @staticmethod
    def test_get_item_transfer_fail(test_client, test_session, exchange_link, token):
        """Test a fail of item transfer due to wrong user opened a link for someone else."""
        # testuser1 follows the link made for testuser2
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                response = test_client.get(exchange_link, headers=headers)
                assert response.status_code == 403
                assert response.json()["detail"] == "Sorry, this link isn't for you"

    @staticmethod
    def test_get_item_unauthorized(test_client, exchange_link, token):
        """Test a fail to get a get view by unauthorized user."""
        response = test_client.get(exchange_link)
        assert response.status_code == 401

    @staticmethod
    def test_get_item_no_transfer_key(test_client, test_session, token):
        """Test a fail of item transfer due to no transfer key."""
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                response = test_client.get("api/v1/get?transfer_key=", headers=headers)
                assert response.status_code == 404

    @staticmethod
    @pytest.mark.parametrize("key", [None, False, True, " ", -1, 0, 1, "-1", "0", "1", "a", "any other string"])
    def test_get_item_wrong_transfer_key(test_client, test_session, token, key):
        """Test a fail of item transfer due to no transfer key."""
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                response = test_client.get(f"api/v1/get?transfer_key={key}", headers=headers)
                assert response.status_code == 401

    @staticmethod
    def test_get_item_invalid_transfer_key(test_client, test_session, token):
        """Test a fail of item transfer due to invalid transfer key."""
        key = create_access_token(1, settings.SECRET_KEY, {"minutes": 1})
        with patch("validators.authentication.session", test_session):
            with patch("views.items.session", test_session):
                headers = {"Authorization": f"Bearer {token}"}
                response = test_client.get(f"api/v1/get?transfer_key={key}", headers=headers)
                assert response.status_code == 400
                assert response.json()["detail"] == "Invalid key"


if __name__ == "__main__":
    pytest.main()
