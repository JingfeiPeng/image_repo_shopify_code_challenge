from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import os
import json
from os.path import join
import logging
import argparse
import sqlite3 as sql
import uuid

UPLOAD_FOLDER = None
IMAGE_TABLE = "Image"
USER_TABLE = "User"

logging.basicConfig(level=logging.WARNING)

# To prevent user from uploading a malicious script
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# initialize flask app
app = Flask(__name__)

CORS(app)


def db():
    assert app.config["DATABASE"]
    conn = sql.connect(app.config["DATABASE"])
    cur = conn.cursor()
    return cur, conn


def setup(uploadFolder: str, database: str, reset=False) -> None:
    UPLOAD_FOLDER = uploadFolder
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["DATABASE"] = database
    if not os.path.isdir(UPLOAD_FOLDER):
        # Create storage folder if not exists
        os.mkdir(UPLOAD_FOLDER)

    cur, conn = db()
    if reset:
        # if reset, clear all images in storage and drop table
        for file in os.listdir(UPLOAD_FOLDER):
            os.remove(join(UPLOAD_FOLDER, file))
        cur.execute(f"DROP TABLE IF EXISTS {IMAGE_TABLE}")
        cur.execute(f"DROP TABLE IF EXISTS {USER_TABLE}")
    else:
        # return if table exists
        cur.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{IMAGE_TABLE}'"
        )
        check_table_exists = cur.fetchone()
        if check_table_exists:
            return

    # initialize table
    # User table
    cur.execute(f"CREATE TABLE {USER_TABLE} (account TEXT PRIMARY KEY)")
    cur.execute(f"INSERT INTO {USER_TABLE} (account) VALUES ('root')")

    # Image table
    cur.execute(
        f"""CREATE TABLE {IMAGE_TABLE} (
            path TEXT PRIMARY KEY, 
            title Text,
            description TEXT, 
            permission TEXT CHECK( permission IN ('PUBLIC', 'PRIVATE') ) NOT NULL,
            owner TEXT NOT NULL,
            FOREIGN KEY(owner) REFERENCES {USER_TABLE}(account)
        )"""
    )
    conn.commit()


def error_response(txt, code):
    """Return a JSON error response based on txt and code"""
    return make_response(jsonify({"description": txt}), code)


def success_response(msg):
    return make_response(jsonify({"message": msg}), 200)


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

    user = request.form.get("user")
    permission = request.form.get("permission")
    description = request.form.get("description")
    if permission != "PUBLIC" and permission != "PRIVATE":
        return error_response("permission field must be 'PUBLIC' or 'private'", 400)
    try:
        cur, conn = db()
        # Creater user if not exists
        cur.execute(f"SELECT account from {USER_TABLE} WHERE account = ?", (user,))
        check_user_exists = cur.fetchone()
        # TODO: Limit the number of images allowed per user
        if not check_user_exists:
            # Create user if user doesn't exist
            cur.execute(
                f"INSERT OR REPLACE INTO {USER_TABLE} (account) VALUES ( ? )", (user,)
            )

        # TODO: possibly have an option to compress image to save size
        _, file_extension = os.path.splitext(imagefile.filename)
        file_name = f"{uuid.uuid4()}{file_extension}"
        imagefile.save(join(app.config["UPLOAD_FOLDER"], secure_filename(file_name)))
        cur.execute(
            f"INSERT OR REPLACE INTO {IMAGE_TABLE} (path, title, description, permission, owner) VALUES (?,?,?,?,?)",
            (file_name, imagefile.filename, description, permission, user),
        )
        conn.commit()
    except Exception as e:
        logging.error(
            f"While updating database for {imagefile.filename}, error: {str(e)}"
        )
        return error_response(
            f"Image saved, error while updating database: {str(e)}", 500
        )

    return success_response(f"saved file {imagefile.filename} as {file_name}")


@app.route("/images", methods=["GET"])
def get_images():
    """"Returns all public images and all images of user regardless of permission"""
    cur, conn = db()
    user = request.args.get("user", default="")
    keywords = request.args.get("keywords", default="")
    if keywords == "":
        cur.execute(
            f"SELECT * from {IMAGE_TABLE} WHERE permission='PUBLIC' OR owner = ?",
            (user,),
        )
    else:
        cur.execute(
            f"""
        SELECT * from {IMAGE_TABLE} 
        WHERE (permission='PUBLIC' 
        OR owner = ?)
        AND (instr(title, ? ) > 0 OR instr(description, ? ) > 0)""",
            (user, keywords, keywords),
        )
    # TODO: have pagination to return maximally X amount of images at once instead of returning all
    # images. Also return the current page number and client can pass an argument for images on page Y,
    # for example, if each page has 20 images, client requesting second page would get from the 20th
    # to 40th image(exclusive) in the fetched sql results
    images = cur.fetchall()
    return json.dumps(images)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="image repo server",
    )
    parser.add_argument(
        "--port",
        help="Port the server will run on",
        default=8081,
        type=int,
    )
    parser.add_argument(
        "--reset",
        help="if set, resets the sql database and clear all images in storage",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--storage_dir",
        type=str,
        help="the storage directory for all image files",
        default=join(os.path.dirname(os.path.realpath(__file__)), "storage"),
    )
    parser.add_argument(
        "--database",
        type=str,
        help="the database file",
        default=join(os.path.dirname(os.path.realpath(__file__)), "database.db"),
    )
    args = parser.parse_args()
    setup(args.storage_dir, args.database, reset=args.reset)
    app.run(port=args.port)
