from os import listdir
from os.path import isfile, join
import aiohttp
import asyncio
import requests
import os

URL = "http://127.0.0.1:8081"


async def post_file(image_path):
    files = {
        "file": open(
            image_path,
            "rb",
        )
    }
    r = requests.post(f"{URL}/image", files=files)
    data = r.json()
    return data


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for f in listdir(
            join(os.path.dirname(os.path.realpath(__file__)), "sample_images")
        ):
            file_path = join(os.path.dirname(os.path.realpath(__file__)), "sample_images", f)
            if isfile(file_path):
                tasks.append(post_file(file_path))
        results = await asyncio.gather(*tasks)
        print(results)

if __name__ == "__main__":
    asyncio.run(main())
