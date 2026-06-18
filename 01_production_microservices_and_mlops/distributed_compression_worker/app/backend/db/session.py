from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.config import DB_HOST, DB_PORT, DB_PASS, DB_USER, DB_NAME
from models.model import metadata, User

SQLALCHEMY_DATABASE_URL = f"mysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# SQLALCHEMY_DATABASE_URL = f"mysql://root:uTnw0PIh65_!@localhost:3306/encode_your_text_db"
# SQLALCHEMY_DATABASE_URL = "mysql://root:uTnw0PIh65_!@localhost:3306/encode_proj_db"#+mysqlconnector

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=50)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# metadata.create_all(engine)  # only for creating table(-s)
# metadata.drop_all(engine)  # only for droping table(-s)

