# Copyright (c) Konica Minolta Business Solutions. All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
from mongoengine import connect

from tagger import DB_HOST, DB_PORT, DB_NAME


class MongoClient:

    def __init__(self):
        connect(DB_NAME, host=DB_HOST, port=DB_PORT)


if __name__ == '__main__':
    client = MongoClient()
