import os

from PIL import Image

from tagger.model.places365_handler import Places365Handler
from tagger.web.app import app

places = Places365Handler('resnet50_places365.pth.tar')
img = Image.open('./data/IMG_20190215_143254591.jpg')
places.predict(img)

# if __name__ == '__main__':
#     app.run(debug=True)
