
# Architecture

### Server:

    - Manages a directory as storage for all image files
    - Handles incoming REST API calls to manage the folder
    - Possibly handle image compression as an option?
    - Use SQL to storage meta data
    - Have Cache to avoid fetching from SQL (use Redis?)
    - Have users table to protect access to images

### Client:

    Script:

    - Client script to send POST request with body as the image to server
    - Use Async to make API call
    - Options allow:

        - individual file path
        - a directory file path

    Web UI:

    - Dropbox to upload image
    - display avaliable images
    - search avaliable images and delete based on keyword, allow filtering out wanted images

### Database:
    - Uses a SQL table for storing image meta_data
    Image table:
     path: str
     description: str
    
## Usage:

Start server:
```
python server/server.py
```

Upload files:
```
python client/post_client.py --file client/sample_images/cat_1.jpg --file client/sample_images2/cat_copied.jpg
```

Upload folders:
```
python client/post_client.py --file client/sample_images/cat_1.jpg --file client/sample_images2/cat_copied.jpg 
```

Or combination:
```
python client/post_client.py --file client/sample_images/cat_1.jpg --dir client/sample_images2/
```