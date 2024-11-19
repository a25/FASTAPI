from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL ='postgrsql://<username>:<password>@<ip-address/hostname>/<database_name>'
SQLALCHEMY_DATABASE_URL = 'postgrsql://postgres:ashish@localhost/fastapi'

engine= create_engine(SQLALCHEMY_DATABASE_URL) # its responsible for connectng sqlalchemy to postgres database

SessionLocal=sessionmaker(engine,autoflush=False)

Base= declarative_base()