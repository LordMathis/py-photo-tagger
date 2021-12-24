# Copyright (c) Konica Minolta Business Solutions. All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
from mongoengine import Document, StringField, FloatField, ListField, EmbeddedDocument, \
    EmbeddedDocumentField


class TagSchema(EmbeddedDocument):
    value = StringField(required=True)
    probability = FloatField(required=True)
    model_name = StringField(required=True)


class LocationSchema(EmbeddedDocument):
    latitude = FloatField()
    longitude = FloatField()
    city = StringField()
    country = StringField()


class PhotoSchema(Document):
    hash = StringField(required=True, primary_key=True)
    filepath = StringField(required=True)
    tags = ListField(EmbeddedDocumentField(TagSchema))
    location = EmbeddedDocument(LocationSchema)


class PossibleTagSchema(Document):
    name = StringField(required=True, primary_key=True)
