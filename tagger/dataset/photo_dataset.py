import os

import filetype
from PIL import Image
from torch.utils.data import Dataset

from tagger import DATA_BASE_PATH


def find_all_images():
    images = []
    for path, _, files in os.walk(DATA_BASE_PATH):
        for file in files:
            filepath = os.path.join(path, file)
            if filetype.is_image(filepath):
                images.append(filepath)
    return images


class PhotoDataset(Dataset):
    def __init__(self, transform=None):
        self.transform = transform
        self._imgs = find_all_images()

    def __len__(self):
        return len(self._imgs)

    def __getitem__(self, idx):
        img_path = self._imgs[idx]
        image = Image.open(img_path)
        if self.transform:
            image = self.transform(image)
        return image, img_path
