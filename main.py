import os

from PIL import Image

from tagger import utils
from tagger.model.places365_handler import Places365Handler
from tagger.web.app import app
from tagger.worker import Worker

places = Places365Handler('resnet50_places365.pth.tar')

json_data = utils.read_json_file('./taggs.json')

worker = Worker(places, json_data)
worker.start()
worker.join()

# if __name__ == '__main__':
#     app.run(debug=True)
