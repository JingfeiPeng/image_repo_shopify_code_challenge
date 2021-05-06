from os import listdir
from os.path import isfile, join
import aiohttp
import asyncio
import argparse
import requests
import os
from utils import URL
import click

# Since the requests are async, set a bound of 30 on the maxnium number of requests that
# can be made at once. Feel free to lower the bound and have sleep method on server's api 
# to test effectiveness
MAX_REQUESTS_AT_ONCE = 30

async def post_file(session, sema, image_path):
    with open(image_path, "rb") as f:
        async with sema, session.post(f"{URL}/image", data={ "file": f }) as r:
            return await r.json()


async def main(directories, files) -> None:
    sema = asyncio.BoundedSemaphore(value=MAX_REQUESTS_AT_ONCE)
    async with aiohttp.ClientSession() as session:
        tasks = []
        if directories:
            for path in directories:
                # each input arg is a list by default
                path = path[0]
                # sends all files at path directory
                for f in listdir(path):
                    file_path = join(path, f)
                    if isfile(file_path):
                        tasks.append(post_file(session, sema, file_path))
        if files:
            for path in files:
                # each input arg is a list by default
                path = path[0]
                if isfile(path):
                    # sends a single file
                    tasks.append(post_file(session, sema, path))
                else:
                    print(f"Error: {path} or {relative_path} is not a valid file path")
        results = await asyncio.gather(*tasks)
        print(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="image repo client for uploading files",
        description="a script to upload images based on a path, can upload individual files or every file in a folder",
    )
    parser.add_argument(
        "--dir",
        help="path to the directory of images to send",
        type=str,
        action='append', nargs='+'
    )
    parser.add_argument(
        "--file",
        help="the path to a file to be uploaded",
        action='append', nargs='+'
    )
    args = parser.parse_args()

    if not args.dir and not args.file:
        # default the directory to be sample images
        args.dir =[[join(os.path.dirname(os.path.realpath(__file__)), "sample_images")]]

    asyncio.run(main(args.dir, args.file))
