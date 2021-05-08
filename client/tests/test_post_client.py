from client import post_client
from os.path import join
import os
import asyncio


def test_post(mocker):
    async def mock_fn(session, sema, image_path, meta_info):
        print("works?")

    mocker.patch(
        'client.post_client.post_file',
        mock_fn
    )

    asyncio.run(post_client.main([
            [join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "sample_images")]
        ], [], {}))

