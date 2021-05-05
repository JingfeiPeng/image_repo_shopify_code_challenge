from flask import Flask
from flask import request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import os
from os.path import join
import json
import argparse

UPLOAD_FOLDER = join(os.path.dirname(os.path.realpath(__file__)), "storage")

# To prevent user from uploading a malicious script
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)

def error_response(txt, code):
    """Return a JSON error response based on txt and code"""
    return json.dumps({
        "code": code,
        "description": txt,
    }), code

def success_response(msg):
    return json.dumps({
        'message': msg,
    })

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# POST request for uploading a single image
@app.route("/image", methods=['POST'])
def post_image():
    """Option to overwrite if file exists"""
    if 'file' not in request.files:
        return error_response("Please supply a field named 'file' as the image to upload", 400)    
    imagefile = request.files['file']
    if imagefile.filename == '' or not allowed_file(imagefile.filename):
        return error_response(f"Please supply a valid file of following types {', '.join(ALLOWED_EXTENSIONS)}", 400)    

    imagefile.save(join(app.config['UPLOAD_FOLDER'], secure_filename(imagefile.filename)))
    return success_response(f"saved file {imagefile.filename}")
    
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
    args = parser.parse_args()

    app.run(port=args.port)
