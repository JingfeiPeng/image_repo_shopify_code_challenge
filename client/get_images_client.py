import argparse
import requests
import os

DEFAULT_USER = "root"
URL = "http://127.0.0.1:8081"

def get_file(user: str, keywords: str):
    r = requests.get(f"{URL}/images", params={'user':user, 'keywords': keywords})
    data = r.json()
    print(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="image repo client for fetching images",
        description="a script to get images from server",
    )
    parser.add_argument(
        "--user",
        help="the user where the uploaded images belong to",
        type=str,
        default=DEFAULT_USER,
    )
    parser.add_argument(
        "--keyword",
        help="search images based on keyword in image file name or description. When not set, returns all possible images",
        type=str,
        default="",
    )
    args = parser.parse_args()

    get_file(args.user, args.keyword)
