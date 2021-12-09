# Copyright (c) Konica Minolta Business Solutions. All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
from mongoengine import Document, StringField, FloatField, ListField, ReferenceField, MapField, EmbeddedDocument, \
    EmbeddedDocumentField


class TagDocument(EmbeddedDocument):
    name = StringField(required=True)
    probability = FloatField(required=True)


class ModelDocument(EmbeddedDocument):
    name = StringField(required=True)
    tags = ListField(EmbeddedDocumentField(TagDocument))


class PhotoDocument(Document):
    filepath = StringField(required=True, primary_key=True)
    models = MapField(EmbeddedDocumentField(ModelDocument))


class PossibleTag(Document):
    name = StringField(required=True, primary_key=True)
