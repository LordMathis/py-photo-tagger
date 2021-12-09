# Copyright (c) Konica Minolta Business Solutions. All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
from mongoengine import Document, StringField, FloatField, ListField, ReferenceField


class TagDocument(Document):
    name: StringField(required=True)
    probability: FloatField(required=True)


class ModelDocument(Document):
    name = StringField(required=True)
    tags = ListField(ReferenceField(TagDocument))


class PhotoDocument(Document):
    path = StringField(required=True)
    models = ListField(ReferenceField(ModelDocument))
