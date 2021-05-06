import argparse
import requests
import os
from utils import URL


def get_file():
    r = requests.get(f"{URL}/images")
    data = r.json()
    print(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="image repo client for fetching images",
        description="a script to get images from server",
    )
    args = parser.parse_args()

    get_file()
