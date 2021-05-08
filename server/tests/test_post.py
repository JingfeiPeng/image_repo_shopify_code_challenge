import os
import tempfile
from os.path import join
import json

import pytest

from server import server

TESTING_IMAGE = "cat_1.jpg"


@pytest.fixture
def client():
    db_fd, server.app.config["DATABASE"] = tempfile.mkstemp()

    with server.app.test_client() as client:
        with server.app.app_context():
            server.setup(
                "./server/test_storage/", server.app.config["DATABASE"], reset=True
            )
        yield client

    os.close(db_fd)
    os.unlink(server.app.config["DATABASE"])


@pytest.fixture
def image():
    with open(
        join(os.path.dirname(os.path.realpath(__file__)), TESTING_IMAGE), "rb"
    ) as f:
        yield f


@pytest.fixture
def cat2():
    with open(
        join(os.path.dirname(os.path.realpath(__file__)), "cat_2.jpg"), "rb"
    ) as f:
        yield f


@pytest.fixture
def cat3():
    with open(
        join(os.path.dirname(os.path.realpath(__file__)), "cat_3.jpg"), "rb"
    ) as f:
        yield f


def test_public_post(client, image):
    """Start with no images"""
    rv = client.get("/images")
    list_of_images = json.loads(rv.data)
    assert len(list_of_images) == 0

    """Post image"""
    rv = client.post(
        "/image",
        data={
            "file": image,
            "user": "test_user",
            "permission": "PUBLIC",
            "description": "Look at this cat",
        },
    )
    assert rv.status_code == 200
    response = json.loads(rv.data)
    assert "saved file cat_1.jpg" in response["message"]

    """get image"""
    rv = client.get("/images")
    list_of_images = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(list_of_images) == 1
    uploaded_image = list_of_images[0]
    assert uploaded_image[1] == TESTING_IMAGE
    assert uploaded_image[2] == "Look at this cat"
    assert uploaded_image[3] == "PUBLIC"
    assert uploaded_image[4] == "test_user"


def test_private_post(client, image):
    """Start with no images"""
    rv = client.get("/images")
    list_of_images = json.loads(rv.data)
    assert len(list_of_images) == 0

    """Post image"""
    rv = client.post(
        "/image",
        data={
            "file": image,
            "user": "prviate_user",
            "permission": "PRIVATE",
            "description": "Look at this cat",
        },
    )
    assert rv.status_code == 200
    response = json.loads(rv.data)
    assert "saved file cat_1.jpg" in response["message"]

    """should get no images since another_user has no access"""
    rv = client.get(
        "/images",
        query_string={
            "user": "another_user",
        },
    )
    list_of_images = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(list_of_images) == 0

    """should get the image since prviate_user made the request """
    rv = client.get("/images", query_string={"user": "prviate_user"})
    list_of_images = json.loads(rv.data)
    assert rv.status_code == 200
    assert len(list_of_images) == 1


def test_searching_images(client, image, cat2, cat3):
    """Start with no images"""
    rv = client.get("/images")
    list_of_images = json.loads(rv.data)
    assert len(list_of_images) == 0

    """Post images, 2 public 1 private"""
    client.post(
        "/image",
        data={
            "file": image,
            "user": "public",
            "permission": "PUBLIC",
            "description": "how is this cat",
        },
    )
    client.post(
        "/image",
        data={
            "file": cat2,
            "user": "public",
            "permission": "PUBLIC",
            "description": "what is this cat",
        },
    )
    client.post(
        "/image",
        data={
            "file": cat3,
            "user": "prviate_user",
            "permission": "PRIVATE",
            "description": "how is this cat",
        },
    )

    """should get only public images"""
    rv = client.get(
        "/images",
        query_string={
            "user": "another_user",
        },
    )
    assert rv.status_code == 200
    list_of_images = json.loads(rv.data)
    assert len(list_of_images) == 2

    """should get all images"""
    rv = client.get(
        "/images",
        query_string={
            "user": "prviate_user",
        },
    )
    assert rv.status_code == 200
    list_of_images = json.loads(rv.data)
    assert len(list_of_images) == 3

    """should get 2 images with description 'how is this cat'"""
    rv = client.get("/images", query_string={"user": "prviate_user", "keywords": "how"})
    assert rv.status_code == 200
    list_of_images = json.loads(rv.data)
    assert len(list_of_images) == 2
    assert "how" in list_of_images[0][2]
    assert "how" in list_of_images[1][2]

    """should get 1 images with description 'how is this cat', since the user 'public'
    doesn't have access to the other private image"""
    rv = client.get("/images", query_string={"user": "public", "keywords": "how"})
    assert rv.status_code == 200
    list_of_images = json.loads(rv.data)
    assert len(list_of_images) == 1
    assert "how" in list_of_images[0][2]
