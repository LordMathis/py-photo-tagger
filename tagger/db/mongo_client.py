# Copyright (c) Konica Minolta Business Solutions. All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
from typing import Dict

from mongoengine import connect

from tagger import DB_HOST, DB_PORT, DB_NAME
from tagger.db.schema import PossibleTag


def init_db():
    connect(DB_NAME, host=DB_HOST, port=DB_PORT)


def populate_tag_list(tags: Dict[int, str]):
    for t in tags.values():
        PossibleTag(name=t).save()
