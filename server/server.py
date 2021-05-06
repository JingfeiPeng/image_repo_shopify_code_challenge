from flask import Flask
from flask import request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import os
from os.path import join
import json
import argparse
import sqlite3 as sql

UPLOAD_FOLDER = join(os.path.dirname(os.path.realpath(__file__)), "storage")
IMAGE_TABLE = "Image"

# To prevent user from uploading a malicious script
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# initialize flask app
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

CORS(app)


def db():
    conn = sql.connect(join(os.path.dirname(os.path.realpath(__file__)), "database.db"))
    cur = conn.cursor()
    return cur, conn


def setup(reset=False) -> None:
    cur, conn = db()
    if reset:
        # if reset, clear all images in storage and drop table
        for file in os.listdir(UPLOAD_FOLDER):
            os.remove(join(UPLOAD_FOLDER, file))
        cur.execute(f"DROP TABLE IF EXISTS {IMAGE_TABLE}")
    else:
        # return if table exists
        cur.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{IMAGE_TABLE}'"
        )
        check_table_exists = cur.fetchone()
        if check_table_exists:
            return

    # initialize table
    cur.execute(f"CREATE TABLE {IMAGE_TABLE} (path TEXT PRIMARY KEY, description TEXT)")
    conn.commit()


def error_response(txt, code):
    """Return a JSON error response based on txt and code"""
    return (
        json.dumps(
            {
                "code": code,
                "description": txt,
            }
        ),
        code,
    )


def success_response(msg):
    return json.dumps(
        {
            "message": msg,
        }
    )


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# POST request for uploading a single image
@app.route("/image", methods=["POST"])
def post_image():
    """Option to overwrite if file exists"""
    if "file" not in request.files:
        return error_response(
            "Please supply a field named 'file' as the image to upload", 400
        )
    imagefile = request.files["file"]
    if imagefile.filename == "" or not allowed_file(imagefile.filename):
        return error_response(
            f"Please supply a valid file of following types {', '.join(ALLOWED_EXTENSIONS)}",
            400,
        )

    cur, conn = db()
    imagefile.save(
        join(app.config["UPLOAD_FOLDER"], secure_filename(imagefile.filename))
    )
    cur.execute(
        f"INSERT INTO {IMAGE_TABLE} (path, description) VALUES (?,?)",
        (imagefile.filename, "default_description"),
    )
    conn.commit()
    return success_response(f"saved file {imagefile.filename}")


@app.route("/images", methods=["GET"])
def get_images():
    cur, conn = db()
    cur.execute(f"SELECT path, description from {IMAGE_TABLE}")
    images = cur.fetchall()
    return json.dumps(images)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="image repo server",
    )
    parser.add_argument(
        "--port",
        help="Port the server will run on.",
        default=8081,
        type=int,
    )
    parser.add_argument(
        "--reset",
        help="if set, resets the sql database and clear all images in storage",
        default=False,
        action="store_true",
    )
    args = parser.parse_args()

    setup(args.reset)
    app.run(port=args.port)
