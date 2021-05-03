
# Architecture

Server:
    - Manages a directory as storage for all image files
    - Handles incoming REST API calls to manage the folder
    - Possibly handle image compression as an option?
    - Use SQL to storage meta data
    - Have Cache to avoid fetching from SQL (use Redis?)
Client:
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
