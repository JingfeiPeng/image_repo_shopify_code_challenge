from ..server import db, UPLOAD_FOLDER
import os

def test_post():
    setup()

    image_files = os.listdir(UPLOAD_FOLDER)
    print(image_files)
    cur, conn = db()
    
