import os
import tempfile
from os.path import join
import json

import pytest

from server import server


@pytest.fixture
def client():
    db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()

    with server.app.test_client() as client:
        with server.app.app_context():
            server.setup("./server/test_storage/",server.app.config['DATABASE'], reset=True)
        yield client

    os.close(db_fd)
    os.unlink(server.app.config['DATABASE'])

@pytest.fixture
def image():
    with open(join(os.path.dirname(os.path.realpath(__file__)), "cat_1.jpg"), "rb") as f:
        yield f

def test_post(client, image):
    print(image)
    """Start with no images"""
    rv = client.get('/images')
    list_of_images = json.loads(rv.data)
    assert len(list_of_images) == 0

    """Post image"""
    rv = client.post('/image', data={
        "file": image,
        "user": 'test_user',
        "permission": "PUBLIC",
        "description": 'Test image',
    })
    assert rv.status_code == 200
    response = json.loads(rv.data)
    assert 'saved file cat_1.jpg' in response['message']
    