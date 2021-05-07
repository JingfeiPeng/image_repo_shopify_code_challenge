# Shopify Image repo code challenge



## Setup:

Python version: 3.7.6

Install dependencies
```
pip install -r requirements.txt
```

Start server:
```
python server/server.py
```


## Usage

Upload files:
```
python client/post_client.py \
    --file client/sample_images/cat_1.jpg \
    --file client/sample_images2/cat_copied.jpg
```

Upload folders:
```
python client/post_client.py \
    --dir client/sample_images/ \
    --dir client/sample_images2/ 
```

Or combination:
```
python client/post_client.py \
    --file client/sample_images/cat_1.jpg \
    --dir client/sample_images2/
```

# Architecture

### Server:

    - Manages a directory as storage for all image files
    - Handles incoming POST API calls to store image
    - Uses SQL to store image meta data and user
    - Has Cache to avoid fetching from SQL
    - Have users table to protect access to images

### Client:

    Script:

    post_client.py:
    - Client script to send POST request with body as the image to server
    - Uses Async to allow large amount of API calls
    - Uses configurable semaphora to avoid making infinity amount of API call at once
    - Options:
        --dir: a directory path, defaults to sample_images
        --file: individual file path
        --private: set all images uploaded by the script to be private, default is public where anyone can access. Private images would only be searchable by the user that uploaded them
        --description: description for all images that are about to be uploaded by the script. To have different description for images. Use the script multiple times
        --user: the user that is uploading the images, defaults to root user
    
    get_images_client.py:
    - Client script to get a list of all avaliable images in the image repo and their meta data
    - Options:
        --user: get images for specified user. This will get all public images and private images for specified user
        --keywords: search images based on keyword. This will find all images with title containing keyword or description containing keyword


### Database:
    - Uses a SQL table for storing image meta_data
    User table:
     account: String
    
    Currently there is no user authenication, to have user authenication, I would store encrypted password in User table and have a login api for giving JWT token if successfully login,
    subsequent requests for storing images will pass the JWT token where other APIs can get user account
    from the token

    Image table:
        path: str
        description: str
        permission: 'PUBLIC' or 'PRIVATE'
        owner: str
        owner references account in User

