"""Test items view."""
import json
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Item, User, main


def test_get_user_items(test_client, test_session, token):
    """Test items get-view sends 200 & items."""
    with patch("validators.authentication.session", test_session):
        with patch("views.items.session", test_session):
            headers = {"Authorization": f"Bearer {token}"}
            response = test_client.get("/api/v1/items", headers=headers)
            assert response.status_code == 200
            assert response.json()


def test_get_user_items_still_works(test_client, test_session, token):
    """Test items get-view sends 200 & items even if there's any other query in the path."""
    with patch("validators.authentication.session", test_session):
        with patch("views.items.session", test_session):
            headers = {"Authorization": f"Bearer {token}"}
            response = test_client.get("/api/v1/items?q=1", headers=headers)
            assert response.status_code == 200
            assert response.json()


def test_create_new_item(test_client, test_session, token):
    """Test create new item."""
    with patch("validators.authentication.session", test_session):
        with patch("views.items.session", test_session):
            headers = {"Authorization": f"Bearer {token}"}
            payload = json.dumps({"title": "new_awesome_item"})
            response = test_client.post("/api/v1/items/new", headers=headers, data=payload)
            assert response.status_code == 201
            assert response.json()


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


def test_delete_one_item(test_client, test_session, token):
    """Test delete one item by id."""
    with patch("validators.authentication.session", test_session):
        with patch("views.items.session", test_session):
            headers = {"Authorization": f"Bearer {token}"}
            response = test_client.delete("/api/v1/items/:1", headers=headers)
            assert response.status_code == 200  # Actually it should be 204
            assert "successfully deleted" in response.json()["message"]


def test_twice_delete_one_item(test_client, test_session, token):
    """Test fail to delete one item twice."""
    with patch("validators.authentication.session", test_session):
        with patch("views.items.session", test_session):
            headers = {"Authorization": f"Bearer {token}"}
            test_client.delete("/api/v1/items/:2", headers=headers)

            response = test_client.delete("/api/v1/items/:2", headers=headers)
            assert response.status_code == 404


if __name__ == "__main__":
    pytest.main()
