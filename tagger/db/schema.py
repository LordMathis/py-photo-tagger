from sqlalchemy import Column, String, Integer, ForeignKey, Float, Boolean, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Photo(Base):
    __tablename__ = 'photos'

    id = Column(String, primary_key=True)
    filepath = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String)
    country = Column(String)

    tags = relationship('PhotoTag')
    model_status = relationship('ModelPhotoStatus')


class Model(Base):
    __tablename__ = 'models'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    version = Column(Integer, default=1)

    tags = relationship('ModelTag')
    photos_status = relationship('ModelPhotoStatus')


class ModelTag(Base):
    __tablename__ = 'model_tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    model_id = Column(Integer, ForeignKey('models.id'))

    photo_tags = relationship('PhotoTag')
    model = relationship('Model', back_populates='tags')


class PhotoTag(Base):
    __tablename__ = 'photo_tags'

    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, ForeignKey('model_tags.id'))
    photo_id = Column(String, ForeignKey('photos.id'))
    probability = Column(Float)

    tag = relationship('ModelTag', back_populates='photo_tags')
    photo = relationship('Photo', back_populates='tags')


class ModelPhotoStatus(Base):

    __tablename__ = 'model_photo_status'

    id = Column(Integer, primary_key=True)
    photo_id = Column(String, ForeignKey('photos.id'))
    model_id = Column(Integer, ForeignKey('models.id'))
    status = Column(Boolean, default=False)
    date = Column(Date)

    photo = relationship('Photo', back_populates='model_status')
    model = relationship('Model', back_populates='photos_status')

