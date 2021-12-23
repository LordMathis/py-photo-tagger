import json
import logging

from torchvision import transforms

centre_crop = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def read_json_file(filepath):
    with open(filepath) as json_data:
        file_data = json.load(json_data)
        return file_data


def write_json_file(filepath, data):
    with open(filepath, 'w') as json_file:
        json_file.write(json.dumps(data, indent=4))


def _init_logger():
    logger_format = "%(asctime)s %(levelname)-8.8s [%(funcName)24s():%(lineno)-3s] %(message)s"
    formatter = logging.Formatter(logger_format)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = _init_logger()
