import argparse
import requests
import os
from utils import URL

DEFAULT_USER = "root"

def get_file(user, keywords):
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
        "--keywords",
        help="search images based on keywords in image file name or description. When not set, returns all possible images",
        type=str,
        default="",
    )
    args = parser.parse_args()

    get_file(args.user, args.keywords)
