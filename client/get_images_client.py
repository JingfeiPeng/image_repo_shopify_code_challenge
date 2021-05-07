import argparse
import requests
import os
from utils import URL

DEFAULT_USER = "root"

def get_file(user):
    r = requests.get(f"{URL}/images", params={'user':user})
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
    args = parser.parse_args()

    get_file(args.user)
