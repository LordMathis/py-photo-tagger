from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tagger.db.schema import Base

engine = create_engine('postgresql://user:example@localhost:5432/phototagger')
Session = sessionmaker(bind=engine)

Base.metadata.create_all()
