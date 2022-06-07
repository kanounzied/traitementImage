import shutil

import requests

UPLOAD_IMAGE_URL: str = "http://localhost:5000/"
GET_IMAGE_URL: str = "http://localhost:5000/"
FILEPATH: str = "./Sydney-Opera-House.jpg"
FILENAME: str = "Sydney-Opera-House.jpg"
TEMP_FILEPATH: str = "./temp.jpg"


# Send POST request to add image
def add_image():
    image = open(FILEPATH, "rb")
    files = {
        'file': (image),
        'Content-Type': 'image/jpg',
    }
    return requests.post(UPLOAD_IMAGE_URL, files=files)


# Copy response image to folder
def save_image_from_response(response):
    with open(TEMP_FILEPATH, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


if __name__ == "__main__":

    print("Send image...")
    # Call POST /uploadImage
    response = add_image()
    # Assert that all good
    assert response.status_code == 200

    # Copy response image to folder
    save_image_from_response(response)

    # Read both images
    imageResponse = open("./temp.jpg", "rb").read()
    realImage = image = open(FILEPATH, "rb").read()

    # Assert that the image is loaded perfectly
    assert len(imageResponse) > 0
    # Assert that the image was resized
    assert len(realImage) > len(imageResponse)

    print("All done!")
