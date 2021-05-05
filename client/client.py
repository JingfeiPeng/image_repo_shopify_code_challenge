from os import listdir
from os.path import isfile, join
import aiohttp
import asyncio
import argparse
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


async def main(path, is_file=False) -> None:
    async with aiohttp.ClientSession() as session:
        tasks = []
        if not is_file:
            # sends all files at path directory
            for f in listdir(path):
                file_path = join(path, f)
                if isfile(file_path):
                    tasks.append(post_file(file_path))
        elif isfile(path):
            # sends a single file
            tasks.append(post_file(path))
        elif isfile(join(os.path.dirname(os.path.realpath(__file__)),path)):
            # allow relative path for a single file
            tasks.append(post_file(join(os.path.dirname(os.path.realpath(__file__)),path)))
        else:
            print(f"ERROR: {path} is not a valid file path")
        results = await asyncio.gather(*tasks)
        print(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="image repo client",
        description="a script to upload images based on a path, can upload individual files or every file in a folder",
    )
    parser.add_argument(
        "--path",
        help="path to the folder of images to send, or a individual file, ",
        default=join(os.path.dirname(os.path.realpath(__file__)), "sample_images"),
        type=str,
    )
    parser.add_argument(
        "--is_file",
        help="whether the fed in path is pointing to a file, by default assumes the path points to a folder",
        default=False, action="store_true"
    )
    args = parser.parse_args()
    asyncio.run(main(args.path, args.is_file))
