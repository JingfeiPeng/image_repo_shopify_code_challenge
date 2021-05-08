from client import post_client
from os.path import join
from os import listdir
import os
import asyncio

SAMPLE_IMAGES_DIR = join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "sample_images",
)
SAMPLE_IMAGES2_DIR = join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "sample_images2",
)


def test_post_directories(mocker):
    posting_files = listdir(SAMPLE_IMAGES_DIR) + listdir(SAMPLE_IMAGES2_DIR)

    async def mock_fn(session, sema, image_path, meta_info):
        _, filename = os.path.split(image_path)
        posting_files.remove(filename)
        return 'ok'

    mocker.patch("client.post_client.post_file", mock_fn)

    asyncio.run(
        post_client.main(
            [[SAMPLE_IMAGES_DIR], [SAMPLE_IMAGES2_DIR]],
            [],
            {},
        )
    )

    assert len(posting_files) == 0

def test_post_files(mocker):
    posting_files = ['cat_1.jpg', 'cat_copied.jpg']

    async def mock_fn(session, sema, image_path, meta_info):
        _, filename = os.path.split(image_path)
        posting_files.remove(filename)
        return 'ok'

    mocker.patch("client.post_client.post_file", mock_fn)

    asyncio.run(
        post_client.main(
            [],
            [[join(SAMPLE_IMAGES_DIR,'cat_1.jpg')], [join(SAMPLE_IMAGES2_DIR,'cat_copied.jpg')]],
            {},
        )
    )

    assert len(posting_files) == 0

def test_post_files_with_meta_data(mocker):
    posting_files = ['cat_1.jpg']

    async def mock_fn(session, sema, image_path, meta_info):
        _, filename = os.path.split(image_path)
        posting_files.remove(filename)
        assert meta_info['user'] == 'jeff'
        assert meta_info['permission'] == 'PRIVATE'
        assert meta_info['description'] == 'describe this cat'
        return 'ok'

    mocker.patch("client.post_client.post_file", mock_fn)

    asyncio.run(
        post_client.main(
            [],
            [[join(SAMPLE_IMAGES_DIR,'cat_1.jpg')]],
            {
                "user": 'jeff',
                "permission": "PRIVATE",
                "description": "describe this cat",
            },
        )
    )

    assert len(posting_files) == 0
